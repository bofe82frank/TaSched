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
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

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
        """Skip the current task and move to next"""
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
                {'task': current_task.title}
            )

        # Advance to next task
        self._advance_to_next_task()

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
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    # ========== Timer Loop ==========

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
            # Schedule next tick
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
            # Schedule next tick
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
                # Continue ticking for gap
                self.timer_id = self.root.after(1000, self._tick)
            else:
                # No gap, advance immediately
                self._advance_to_next_task()
        else:
            # Manual advance - stop here
            self.is_running = False

    def _advance_to_next_task(self):
        """Advance to the next task in the schedule"""
        has_next = self.schedule.advance_to_next_task()

        if has_next:
            # Check gap again before starting
            if self.schedule.gap_between_tasks > 0 and self.gap_countdown == 0:
                self.gap_countdown = self.schedule.gap_between_tasks
                self.timer_id = self.root.after(1000, self._tick)
            else:
                self._start_next_task()
        else:
            # No more tasks, schedule complete
            self._complete_schedule()

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

        # Continue timer loop
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
