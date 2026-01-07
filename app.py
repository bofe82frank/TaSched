"""
TaSched - Task Scheduler & Countdown Orchestrator
Main Application Entry Point
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add tasched directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tasched.constants import *
from tasched.core.models import Task, Schedule, Settings
from tasched.core.scheduler_engine import SchedulerEngine
from tasched.services.theme_service import get_theme_service
from tasched.services.resource_service import get_resource_service
from tasched.services.storage_service import get_storage_service
from tasched.services.log_service import get_log_service
from tasched.services.audio_service import get_audio_service
from tasched.ui.run_window import RunWindow
from tasched.ui.alert_windows import WarningPopup, TimeUpWindow
from tasched.ui.setup_window import SetupWindow


class TaSchedApp:
    """Main TaSched Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_FULL_NAME)
        self.root.state('zoomed')  # Maximized window on launch

        # Services
        self.theme = get_theme_service()
        self.resource = get_resource_service()
        self.storage = get_storage_service()
        self.log = get_log_service()
        self.audio = get_audio_service()

        # Load settings
        self.settings = self.storage.load_settings()
        self.theme.set_theme(self.settings.theme)

        # Scheduler engine
        self.scheduler = SchedulerEngine(self.root)
        self.scheduler.set_tick_callback(self._on_tick)
        self.scheduler.set_task_complete_callback(self._on_task_complete)
        self.scheduler.set_schedule_complete_callback(self._on_schedule_complete)
        self.scheduler.set_warning_callback(self._on_warning)
        self.scheduler.set_timeup_callback(self._on_timeup)

        # Windows
        self.run_window = None
        self.warning_popup = WarningPopup(self.root)
        self.timeup_window = TimeUpWindow(self.root)

        # Configure root window
        self._setup_root()

        # Set icon
        icon_path = self.resource.get_image(WAEC_ICON)
        if icon_path:
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Log startup
        self.log.info(f"{APP_NAME} v{APP_VERSION} started")

    def _setup_root(self):
        """Configure root window"""
        self.root.configure(bg=self.theme.background)

        # Create Setup Window
        self.setup_window = SetupWindow(self.root, on_start_callback=self._start_from_setup)
        self.setup_window.pack(fill=tk.BOTH, expand=True)

    def _start_from_setup(self, schedule: Schedule):
        """Start schedule from setup window"""
        # Load into scheduler
        self.scheduler.load_schedule(schedule)

        # Create run window
        self.run_window = RunWindow(
            self.root,
            on_pause_callback=self.scheduler.pause,
            on_resume_callback=self.scheduler.resume,
            on_skip_callback=self.scheduler.skip_task,
            on_force_next_callback=self.scheduler.force_next_task,
            on_stop_callback=self._stop_schedule
        )

        # Hide setup window
        self.root.withdraw()

        # Start schedule
        self.scheduler.start()

    def _on_tick(self, schedule, current_task):
        """Handle timer tick"""
        if self.run_window:
            next_task = self.scheduler.get_next_task()
            self.run_window.update(schedule, current_task, next_task)

    def _on_task_complete(self, task):
        """Handle task completion"""
        print(f"Task completed: {task.title}")

    def _on_schedule_complete(self, schedule):
        """Handle schedule completion"""
        if self.run_window:
            self.run_window.destroy()
            self.run_window = None

        self.root.deiconify()

        messagebox.showinfo(
            "Schedule Complete",
            f"Schedule '{schedule.name}' completed successfully!\n\n"
            f"Total tasks: {len(schedule.tasks)}"
        )

    def _on_warning(self, task, remaining_seconds):
        """Handle warning event"""
        next_task = self.scheduler.get_next_task()
        next_title = next_task.title if next_task else None
        self.warning_popup.show(task, remaining_seconds, next_title)

    def _on_timeup(self, task):
        """Handle time-up event"""
        next_task = self.scheduler.get_next_task()
        next_title = next_task.title if next_task else None
        self.timeup_window.show(task, task.display.fullscreen_timeup, next_title)

    def _stop_schedule(self):
        """Stop the current schedule"""
        result = messagebox.askyesno(
            "Stop Schedule",
            "Are you sure you want to stop this schedule?"
        )

        if result:
            self.scheduler.stop()

            if self.run_window:
                self.run_window.destroy()
                self.run_window = None

            self.root.deiconify()

    def run(self):
        """Run the application"""
        self.root.mainloop()

    def cleanup(self):
        """Clean up resources on exit"""
        self.scheduler.cleanup()
        self.audio.cleanup()
        self.log.info(f"{APP_NAME} closed")


def main():
    """Application entry point"""
    try:
        app = TaSchedApp()
        app.run()
        app.cleanup()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
