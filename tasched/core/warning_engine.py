"""
TaSched - Warning Engine
Evaluates warning thresholds and triggers warning events
"""

from typing import Callable, List, Set
from tasched.core.models import Task


class WarningEngine:
    """
    Monitors task countdown and triggers warnings at configured thresholds
    """

    def __init__(self):
        # Track which warnings have been triggered for current task
        self.triggered_warnings: Set[int] = set()
        self.current_task_id: str = None
        self.on_warning_callback: Callable = None
        self.on_timeup_callback: Callable = None

    def set_warning_callback(self, callback: Callable):
        """
        Set callback for warning events

        Args:
            callback: Function to call when warning is triggered
                     Signature: callback(task, remaining_seconds)
        """
        self.on_warning_callback = callback

    def set_timeup_callback(self, callback: Callable):
        """
        Set callback for time-up events

        Args:
            callback: Function to call when time is up
                     Signature: callback(task)
        """
        self.on_timeup_callback = callback

    def reset_for_task(self, task: Task):
        """
        Reset warning state for a new task

        Args:
            task: The task to monitor
        """
        self.triggered_warnings.clear()
        self.current_task_id = task.id

    def evaluate(self, task: Task) -> bool:
        """
        Evaluate warning conditions for a task

        Args:
            task: The task to evaluate

        Returns:
            True if time is up, False otherwise
        """
        # Reset if different task
        if self.current_task_id != task.id:
            self.reset_for_task(task)

        remaining = task.remaining_seconds

        # Check for time-up
        if remaining <= 0:
            if self.on_timeup_callback:
                self.on_timeup_callback(task)
            return True

        # Check warning thresholds
        warning_points = task.get_warning_thresholds()

        for threshold in warning_points:
            # Trigger warning if:
            # 1. We haven't triggered this warning yet
            # 2. Remaining time is <= threshold
            # 3. Remaining time is > (threshold - 2) to avoid multiple triggers
            if (threshold not in self.triggered_warnings and
                remaining <= threshold and
                remaining > (threshold - 2)):

                self.triggered_warnings.add(threshold)

                if self.on_warning_callback:
                    self.on_warning_callback(task, remaining)

        return False

    def should_show_warning(self, task: Task, threshold: int) -> bool:
        """
        Check if a warning should be shown for a specific threshold

        Args:
            task: The task
            threshold: The warning threshold in seconds

        Returns:
            True if warning should be shown, False if already triggered
        """
        return (threshold not in self.triggered_warnings and
                task.remaining_seconds <= threshold)

    def clear_warnings(self):
        """Clear all triggered warnings"""
        self.triggered_warnings.clear()
        self.current_task_id = None
