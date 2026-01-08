"""
TaSched - Scheduler Engine
State machine and execution loop for running schedules
"""

from typing import Callable, Optional
import tkinter as tk

from tasched.core.models import Schedule, Task
from tasched.core.warning_engine import WarningEngine
from tasched.constants import *
from tasched.services.log_service import get_log_service
from tasched.services.storage_service import get_storage_service


class SchedulerEngine:
    """
    Core scheduler engine - manages schedule execution with state machine
    Uses Tkinter's after() for UI-safe timer updates
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.schedule: Optional[Schedule] = None
        self.warning_engine = WarningEngine()
        self.log_service = get_log_service()
        self.storage_service = get_storage_service()

        # Timer control
        self.timer_id = None
        self.is_running = False
        self.gap_countdown = 0

        # Callbacks
        self.on_tick_callback: Callable = None
        self.on_task_complete_callback: Callable = None
        self.on_schedule_complete_callback: Callable = None
        self.on_warning_callback: Callable = None
        self.on_timeup_callback: Callable = None

        # Configure warning engine callbacks
        self.warning_engine.set_warning_callback(self._handle_warning)
        self.warning_engine.set_timeup_callback(self._handle_timeup)

    # ========== Callback Registration ==========

    def set_tick_callback(self, callback: Callable):
        """Set callback for every timer tick (1 second)"""
        self.on_tick_callback = callback

    def set_task_complete_callback(self, callback: Callable):
        """Set callback for task completion"""
        self.on_task_complete_callback = callback

    def set_schedule_complete_callback(self, callback: Callable):
        """Set callback for schedule completion"""
        self.on_schedule_complete_callback = callback

    def set_warning_callback(self, callback: Callable):
        """Set callback for warning events"""
        self.on_warning_callback = callback

    def set_timeup_callback(self, callback: Callable):
        """Set callback for time-up events"""
        self.on_timeup_callback = callback

    # ========== Schedule Control ==========

    def load_schedule(self, schedule: Schedule):
        """Load a schedule for execution"""
        self.schedule = schedule
        self.schedule.reset()
        self.log_service.log_schedule_start(schedule.name, schedule.id)

    def start(self, from_task_index: int = 0):
        """
        Start schedule execution

        Args:
            from_task_index: Start from specific task index (default: 0)
        """
        if not self.schedule:
            self.log_service.error("Cannot start: No schedule loaded")
            return

        if not self.schedule.tasks:
            self.log_service.error("Cannot start: Schedule has no tasks")
            return

        # Set starting task
        self.schedule.current_task_index = from_task_index
        self.schedule.start()

        # Start first task
        current_task = self.schedule.get_current_task()
        if current_task:
            current_task.start()
            self.warning_engine.reset_for_task(current_task)
            self.log_service.log_task_start(current_task.title, current_task.id)

            # Log to database
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "schedule_started",
                {'from_task_index': from_task_index}
            )

        # Start timer loop
        self.is_running = True
        self._tick()

    def pause(self):
        """Pause the current schedule"""
        if self.schedule:
            self.schedule.pause()
            self.is_running = False

            current_task = self.schedule.get_current_task()
            if current_task:
                self.log_service.log_task_paused(current_task.title)
                self.storage_service.log_event(
                    self.schedule.id,
                    self.schedule.name,
                    "schedule_paused",
                    {'task': current_task.title}
                )

            # Cancel timer
            self._cancel_timer()

    def resume(self):
        """Resume the paused schedule"""
        if self.schedule and self.schedule.state == SCHEDULE_STATE_PAUSED:
            self.schedule.resume()
            self.is_running = True

            current_task = self.schedule.get_current_task()
            if current_task:
                self.log_service.log_task_resumed(current_task.title)
                self.storage_service.log_event(
                    self.schedule.id,
                    self.schedule.name,
                    "schedule_resumed",
                    {'task': current_task.title}
                )

            # Restart timer loop
            self._tick()

    def skip_task(self):
        """
        Skip the current task and move to next.
        If next task has absolute_start_time, waits until that time.
        Otherwise, advances immediately.
        """
        if not self.schedule:
            return

        current_task = self.schedule.get_current_task()
        if current_task:
            current_task.skip()
            self.log_service.log_task_skipped(current_task.title)
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "task_skipped",
                {'task': current_task.title, 'action': 'skip_and_wait'}
            )

        # Advance to next task (will respect absolute time if set)
        self._advance_to_next_task(wait_for_absolute_time=True)

    def force_next_task(self):
        """
        Force immediate start of next task (Next Task button).
        Adjusts all remaining tasks' start times relative to current clock time.
        """
        if not self.schedule:
            return

        current_task = self.schedule.get_current_task()
        if current_task:
            current_task.skip()
            self.log_service.log_task_skipped(current_task.title)
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "task_forced_next",
                {'task': current_task.title, 'action': 'force_and_adjust'}
            )

        # Adjust remaining tasks' absolute times based on current time
        self._adjust_remaining_task_times()

        # Advance to next task immediately (ignore absolute time)
        self._advance_to_next_task(wait_for_absolute_time=False)

    def stop(self):
        """Stop the schedule execution"""
        if self.schedule:
            self.schedule.cancel()
            self.is_running = False

            self.log_service.log_schedule_end(
                self.schedule.name,
                self.schedule.id,
                "cancelled"
            )
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "schedule_cancelled",
                {}
            )

            # Cancel timer
            self._cancel_timer()

    # ========== Timer Loop ==========

    def _cancel_timer(self):
        """Cancel the current timer callback if it exists"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        """Execute one timer tick (called every second)"""
        if not self.is_running or not self.schedule:
            return

        # Handle gap between tasks
        if self.gap_countdown > 0:
            self.gap_countdown -= 1
            if self.gap_countdown == 0:
                # Gap complete, start next task
                self._start_next_task()
            else:
                # Schedule next tick - cancel existing timer first
                self._cancel_timer()
                self.timer_id = self.root.after(1000, self._tick)
            return

        # Get current task
        current_task = self.schedule.get_current_task()
        if not current_task:
            # No current task, schedule complete
            self._complete_schedule()
            return

        # Tick the task (decrement remaining time)
        time_is_up = current_task.tick()

        # Evaluate warnings
        self.warning_engine.evaluate(current_task)

        # Trigger tick callback
        if self.on_tick_callback:
            self.on_tick_callback(self.schedule, current_task)

        # Check if task is complete
        if time_is_up:
            self._handle_task_complete(current_task)
        else:
            # Schedule next tick - cancel existing timer first
            self._cancel_timer()
            self.timer_id = self.root.after(1000, self._tick)

    def _handle_task_complete(self, task: Task):
        """Handle task completion"""
        task.complete()
        self.log_service.log_task_end(task.title, task.id, "completed")
        self.storage_service.log_event(
            self.schedule.id,
            self.schedule.name,
            "task_completed",
            {'task': task.title, 'duration': task.duration_seconds}
        )

        # Trigger task complete callback
        if self.on_task_complete_callback:
            self.on_task_complete_callback(task)

        # Check if auto-advance is enabled
        if self.schedule.auto_advance:
            # Check if there's a gap
            if self.schedule.gap_between_tasks > 0:
                self.gap_countdown = self.schedule.gap_between_tasks
                # Continue ticking for gap - cancel existing timer first
                self._cancel_timer()
                self.timer_id = self.root.after(1000, self._tick)
            else:
                # No gap, advance immediately
                self._advance_to_next_task()
        else:
            # Manual advance - stop here
            self.is_running = False

    def _advance_to_next_task(self, wait_for_absolute_time=False):
        """
        Advance to the next task in the schedule

        Args:
            wait_for_absolute_time: If True and next task has absolute_start_time,
                                   wait until that clock time before starting
        """
        has_next = self.schedule.advance_to_next_task()

        if has_next:
            next_task = self.schedule.get_current_task()

            # Check if we need to wait for absolute start time
            if wait_for_absolute_time and next_task and next_task.absolute_start_time:
                seconds_until_start = self._calculate_wait_time(next_task.absolute_start_time)

                if seconds_until_start > 0:
                    # Set gap countdown to wait until absolute time - cancel existing timer first
                    self.gap_countdown = seconds_until_start
                    self.log_service.info(f"Waiting {seconds_until_start}s until {next_task.absolute_start_time} for '{next_task.title}'")
                    self._cancel_timer()
                    self.timer_id = self.root.after(1000, self._tick)
                    return

            # Check gap before starting
            if self.schedule.gap_between_tasks > 0 and self.gap_countdown == 0:
                self.gap_countdown = self.schedule.gap_between_tasks
                self._cancel_timer()
                self.timer_id = self.root.after(1000, self._tick)
            else:
                self._start_next_task()
        else:
            # No more tasks, schedule complete
            self._complete_schedule()

    def _calculate_wait_time(self, absolute_time_str: str) -> int:
        """
        Calculate seconds to wait until absolute time (HH:MM format)

        Returns:
            Seconds until target time (0 if time has passed or is now)
        """
        from datetime import datetime, time as dt_time

        try:
            # Parse target time
            target_hour, target_minute = map(int, absolute_time_str.split(':'))
            now = datetime.now()
            target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            # If target time has already passed today, it's for tomorrow (return 0 to start now)
            if target <= now:
                return 0

            # Calculate difference
            diff = (target - now).total_seconds()
            return int(diff)
        except Exception as e:
            self.log_service.error(f"Error calculating wait time for '{absolute_time_str}': {e}")
            return 0

    def _adjust_remaining_task_times(self):
        """
        Adjust absolute start times of all remaining tasks based on current time.
        Called when Next Task button is used to force immediate progression.
        """
        from datetime import datetime, timedelta

        if not self.schedule:
            return

        current_index = self.schedule.current_task_index
        tasks = self.schedule.tasks

        # Start from next task
        next_index = current_index + 1
        if next_index >= len(tasks):
            return

        # Calculate cumulative duration from current time
        now = datetime.now()
        cumulative_time = now

        for i in range(next_index, len(tasks)):
            task = tasks[i]

            # Set absolute start time to cumulative time
            task.absolute_start_time = cumulative_time.strftime("%H:%M")

            # Add this task's duration for next task's start
            cumulative_time += timedelta(seconds=task.duration_seconds)

            # Add gap if configured
            if self.schedule.gap_between_tasks > 0:
                cumulative_time += timedelta(seconds=self.schedule.gap_between_tasks)

        self.log_service.info(f"Adjusted remaining {len(tasks) - next_index} task start times from {now.strftime('%H:%M')}")

    def _start_next_task(self):
        """Start the next task"""
        next_task = self.schedule.get_current_task()
        if next_task:
            next_task.start()
            self.warning_engine.reset_for_task(next_task)
            self.log_service.log_task_start(next_task.title, next_task.id)
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "task_started",
                {'task': next_task.title}
            )

        # Continue timer loop - cancel existing timer first
        self._cancel_timer()
        self.timer_id = self.root.after(1000, self._tick)

    def _complete_schedule(self):
        """Handle schedule completion"""
        if self.schedule:
            self.schedule.complete()
            self.is_running = False

            self.log_service.log_schedule_end(
                self.schedule.name,
                self.schedule.id,
                "completed"
            )
            self.storage_service.log_event(
                self.schedule.id,
                self.schedule.name,
                "schedule_completed",
                {}
            )

            # Trigger schedule complete callback
            if self.on_schedule_complete_callback:
                self.on_schedule_complete_callback(self.schedule)

    def _handle_warning(self, task: Task, remaining_seconds: int):
        """Handle warning event from warning engine"""
        self.log_service.log_warning(task.title, remaining_seconds)

        if self.on_warning_callback:
            self.on_warning_callback(task, remaining_seconds)

    def _handle_timeup(self, task: Task):
        """Handle time-up event from warning engine"""
        self.log_service.log_timeup(task.title)

        if self.on_timeup_callback:
            self.on_timeup_callback(task)

    # ========== Status Methods ==========

    def get_current_task(self) -> Optional[Task]:
        """Get the currently running task"""
        if self.schedule:
            return self.schedule.get_current_task()
        return None

    def get_next_task(self) -> Optional[Task]:
        """Get the next task in queue"""
        if self.schedule:
            return self.schedule.get_next_task()
        return None

    def is_schedule_running(self) -> bool:
        """Check if a schedule is currently running"""
        return self.is_running and self.schedule is not None

    def cleanup(self):
        """Clean up resources"""
        self.stop()
        self.schedule = None
        self.warning_engine.clear_warnings()
