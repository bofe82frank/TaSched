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


class TaSchedApp:
    """Main TaSched Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_FULL_NAME)
        self.root.geometry("800x600")

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
        self._create_simple_setup_ui()

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

    def _create_simple_setup_ui(self):
        """Create a simple setup UI for testing"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.theme.background, height=100)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=APP_FULL_NAME,
            font=(FONT_FAMILY, 28, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_1
        )
        title_label.pack()

        tagline_label = tk.Label(
            header_frame,
            text=APP_TAGLINE,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            bg=self.theme.background,
            fg=self.theme.accent_3
        )
        tagline_label.pack()

        # Main content
        content_frame = tk.Frame(self.root, bg=self.theme.background)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Quick start section
        quick_label = tk.Label(
            content_frame,
            text="Quick Start Demo",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
            **self.theme.get_label_style()
        )
        quick_label.pack(pady=(0, 20))

        info_label = tk.Label(
            content_frame,
            text="Click the button below to start a demo schedule with 3 short tasks\n"
                 "(15 seconds each with 5-second warnings)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            **self.theme.get_label_style(),
            justify=tk.CENTER
        )
        info_label.pack(pady=10)

        # Demo button
        demo_button = tk.Button(
            content_frame,
            text="▶ Start Demo Schedule",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
            command=self._start_demo,
            **self.theme.get_button_style(),
            width=25,
            height=2
        )
        demo_button.pack(pady=30)

        # Theme selector
        theme_frame = tk.Frame(content_frame, bg=self.theme.background)
        theme_frame.pack(pady=20)

        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            **self.theme.get_label_style()
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 10))

        for theme_name in ["WAEC", "Corporate", "Indigenous"]:
            btn = tk.Button(
                theme_frame,
                text=theme_name,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                command=lambda t=theme_name: self._change_theme(t),
                bg=self.theme.accent_1 if theme_name == self.settings.theme else self.theme.background,
                fg=self.theme.primary_text,
                relief='flat',
                bd=1,
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Footer
        footer_label = tk.Label(
            self.root,
            text=f"{APP_NAME} v{APP_VERSION} | {COMPANY} - {DEPARTMENT}",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            bg=self.theme.background,
            fg=self.theme.footer
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def _change_theme(self, theme_name: str):
        """Change application theme"""
        self.theme.set_theme(theme_name)
        self.settings.theme = theme_name
        self.storage.save_settings(self.settings)

        # Recreate UI with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self._setup_root()
        self._create_simple_setup_ui()

    def _start_demo(self):
        """Start a demo schedule"""
        # Create demo tasks
        task1 = Task(
            title="Task 1: Reading",
            duration_seconds=15,
            warning_points_seconds=[5],
            mode=TASK_MODE_SEQUENTIAL
        )

        task2 = Task(
            title="Task 2: Writing",
            duration_seconds=15,
            warning_points_seconds=[5],
            mode=TASK_MODE_SEQUENTIAL
        )

        task3 = Task(
            title="Task 3: Break Time",
            duration_seconds=15,
            warning_points_seconds=[5],
            mode=TASK_MODE_SEQUENTIAL
        )

        # Create schedule
        schedule = Schedule(
            name="Demo Schedule",
            auto_advance=True,
            gap_between_tasks=0
        )
        schedule.add_task(task1)
        schedule.add_task(task2)
        schedule.add_task(task3)

        # Save schedule
        self.storage.save_schedule(schedule)

        # Load into scheduler
        self.scheduler.load_schedule(schedule)

        # Create run window
        self.run_window = RunWindow(
            self.root,
            on_pause_callback=self.scheduler.pause,
            on_resume_callback=self.scheduler.resume,
            on_skip_callback=self.scheduler.skip_task,
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
