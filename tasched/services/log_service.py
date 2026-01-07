"""
TaSched - Logging Service
Append-only text logging for debugging and audit trail
"""

import os
from datetime import datetime
from pathlib import Path
from tasched.services.resource_service import get_resource_service


class LogService:
    """
    Simple text-based logging service
    """

    def __init__(self, log_file: str = None):
        resource_service = get_resource_service()

        if log_file:
            self.log_file = log_file
        else:
            self.log_file = resource_service.get_data_file("logs.txt")

        # Ensure log file exists
        Path(self.log_file).touch(exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """
        Write a log entry

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")

    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")

    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")

    def debug(self, message: str):
        """Log debug message"""
        self.log(message, "DEBUG")

    def log_schedule_start(self, schedule_name: str, schedule_id: str):
        """Log schedule start event"""
        self.info(f"Schedule started: {schedule_name} (ID: {schedule_id})")

    def log_schedule_end(self, schedule_name: str, schedule_id: str, status: str):
        """Log schedule end event"""
        self.info(f"Schedule ended: {schedule_name} (ID: {schedule_id}) - Status: {status}")

    def log_task_start(self, task_name: str, task_id: str):
        """Log task start event"""
        self.info(f"Task started: {task_name} (ID: {task_id})")

    def log_task_end(self, task_name: str, task_id: str, status: str):
        """Log task end event"""
        self.info(f"Task ended: {task_name} (ID: {task_id}) - Status: {status}")

    def log_task_paused(self, task_name: str):
        """Log task pause event"""
        self.info(f"Task paused: {task_name}")

    def log_task_resumed(self, task_name: str):
        """Log task resumed event"""
        self.info(f"Task resumed: {task_name}")

    def log_task_skipped(self, task_name: str):
        """Log task skip event"""
        self.warning(f"Task skipped: {task_name}")

    def log_warning(self, task_name: str, remaining_seconds: int):
        """Log warning popup event"""
        self.info(f"Warning triggered for task '{task_name}' - {remaining_seconds}s remaining")

    def log_timeup(self, task_name: str):
        """Log time-up event"""
        self.info(f"Time-up for task: {task_name}")

    def log_error_event(self, error_message: str, context: str = ""):
        """Log error with context"""
        if context:
            self.error(f"{context}: {error_message}")
        else:
            self.error(error_message)

    def get_recent_logs(self, lines: int = 100) -> str:
        """
        Get recent log entries

        Args:
            lines: Number of lines to retrieve

        Returns:
            Recent log content
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent)
        except Exception as e:
            return f"Error reading logs: {e}"

    def clear_logs(self):
        """Clear all log entries"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
            self.info("Log file cleared")
        except Exception as e:
            print(f"Error clearing logs: {e}")

    def export_logs(self, export_path: str) -> bool:
        """
        Export logs to a different file

        Args:
            export_path: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as source:
                content = source.read()

            with open(export_path, 'w', encoding='utf-8') as dest:
                dest.write(content)

            self.info(f"Logs exported to {export_path}")
            return True
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            return False


# Global log service instance
_log_service = None


def get_log_service() -> LogService:
    """
    Get or create the global log service instance

    Returns:
        LogService instance
    """
    global _log_service
    if _log_service is None:
        _log_service = LogService()
    return _log_service
