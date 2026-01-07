"""
TaSched - Run Window
Main timer display window during schedule execution
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from tasched.core.models import Schedule, Task
from tasched.core.time_service import TimeService
from tasched.services.theme_service import get_theme_service
from tasched.services.resource_service import get_resource_service
from tasched.constants import *


class RunWindow:
    """
    Main countdown timer window displayed during schedule execution
    """

    def __init__(self, parent: tk.Tk, on_pause_callback=None, on_resume_callback=None,
                 on_skip_callback=None, on_stop_callback=None):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.theme = get_theme_service()
        self.resource = get_resource_service()
        self.time_service = TimeService()

        # Callbacks
        self.on_pause_callback = on_pause_callback
        self.on_resume_callback = on_resume_callback
        self.on_skip_callback = on_skip_callback
        self.on_stop_callback = on_stop_callback

        # State
        self.is_paused = False
        self.is_fullscreen = True

        # Configure window
        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        """Configure window properties"""
        self.window.title(f"{APP_NAME} - Running")
        self.window.geometry(f"{RUN_WINDOW_WIDTH}x{RUN_WINDOW_HEIGHT}")
        self.window.configure(bg=self.theme.background)

        # Set icon
        icon_path = self.resource.get_image(WAEC_ICON)
        if icon_path:
            try:
                self.window.iconbitmap(icon_path)
            except Exception:
                pass

        # Start in fullscreen
        self.window.attributes('-fullscreen', True)

        # Bind keys
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.window.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.window.bind('<space>', lambda e: self.toggle_pause())

        # Protocol for window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Create UI widgets"""
        # Main container
        main_frame = tk.Frame(self.window, bg=self.theme.background)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar (schedule name and clock)
        top_frame = tk.Frame(main_frame, bg=self.theme.background, height=60)
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        top_frame.pack_propagate(False)

        self.schedule_label = tk.Label(
            top_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_1
        )
        self.schedule_label.pack(side=tk.LEFT)

        self.clock_label = tk.Label(
            top_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_XLARGE, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_3
        )
        self.clock_label.pack(side=tk.RIGHT)

        # Center area (timer and task info)
        center_frame = tk.Frame(main_frame, bg=self.theme.background)
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Task title
        self.task_title_label = tk.Label(
            center_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_TITLE, 'bold'),
            bg=self.theme.background,
            fg=self.theme.primary_text
        )
        self.task_title_label.pack(pady=(40, 20))

        # Countdown timer (large)
        self.countdown_label = tk.Label(
            center_frame,
            text="00:00:00",
            font=(FONT_FAMILY, FONT_SIZE_CLOCK, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_3
        )
        self.countdown_label.pack(pady=20)

        # Status message
        self.status_label = tk.Label(
            center_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_XLARGE, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_1
        )
        self.status_label.pack(pady=10)

        # Next task info
        self.next_task_label = tk.Label(
            center_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            bg=self.theme.background,
            fg=self.theme.primary_text
        )
        self.next_task_label.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            center_frame,
            orient=tk.HORIZONTAL,
            length=600,
            mode='determinate'
        )
        self.progress.pack(pady=20)

        # Control buttons
        button_frame = tk.Frame(center_frame, bg=self.theme.background)
        button_frame.pack(pady=30)

        self.pause_button = tk.Button(
            button_frame,
            text="⏸ Pause",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self.toggle_pause,
            **self.theme.get_button_style(),
            width=12
        )
        self.pause_button.pack(side=tk.LEFT, padx=10)

        skip_button = tk.Button(
            button_frame,
            text="⏭ Skip Task",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self._on_skip,
            **self.theme.get_button_style(),
            width=12
        )
        skip_button.pack(side=tk.LEFT, padx=10)

        stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self._on_stop,
            bg=self.theme.accent_2,
            fg=self.theme.primary_text,
            activebackground=self.theme.accent_3,
            activeforeground=self.theme.background,
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            width=12
        )
        stop_button.pack(side=tk.LEFT, padx=10)

        # Bottom bar (help text)
        bottom_frame = tk.Frame(main_frame, bg=self.theme.background, height=40)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        bottom_frame.pack_propagate(False)

        help_text = "F11: Toggle Fullscreen | Space: Pause/Resume | ESC: Exit Fullscreen"
        help_label = tk.Label(
            bottom_frame,
            text=help_text,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            bg=self.theme.background,
            fg=self.theme.footer
        )
        help_label.pack()

        # Update clock periodically
        self._update_clock()

    def update(self, schedule: Schedule, current_task: Task, next_task: Optional[Task] = None):
        """Update display with current schedule state"""
        # Update schedule name
        self.schedule_label.config(text=schedule.name)

        # Update task title
        self.task_title_label.config(text=current_task.title)

        # Update countdown
        remaining = current_task.remaining_seconds
        countdown_text = self.time_service.format_seconds(remaining)
        self.countdown_label.config(text=countdown_text)

        # Update status
        status_text = self.time_service.get_friendly_time_remaining(remaining)
        self.status_label.config(text=status_text)

        # Update next task info
        if next_task:
            next_text = f"Next: {next_task.title} ({self.time_service.format_duration(next_task.duration_seconds, short=True)})"
            self.next_task_label.config(text=next_text)
        else:
            self.next_task_label.config(text="Last task in schedule")

        # Update progress bar
        if current_task.duration_seconds > 0:
            progress_value = ((current_task.duration_seconds - remaining) / current_task.duration_seconds) * 100
            self.progress['value'] = progress_value

        # Color coding based on time remaining
        if remaining <= 60:
            self.countdown_label.config(fg=self.theme.accent_2)  # Red for last minute
        elif remaining <= 300:
            self.countdown_label.config(fg="#FFA500")  # Orange for last 5 minutes
        else:
            self.countdown_label.config(fg=self.theme.accent_3)  # Normal color

    def _update_clock(self):
        """Update the clock display"""
        current_time = self.time_service.get_current_time()
        self.clock_label.config(text=current_time)
        self.window.after(1000, self._update_clock)

    def toggle_pause(self):
        """Toggle pause/resume"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_button.config(text="▶ Resume")
            if self.on_pause_callback:
                self.on_pause_callback()
        else:
            self.pause_button.config(text="⏸ Pause")
            if self.on_resume_callback:
                self.on_resume_callback()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)

    def _on_skip(self):
        """Handle skip button"""
        if self.on_skip_callback:
            self.on_skip_callback()

    def _on_stop(self):
        """Handle stop button"""
        if self.on_stop_callback:
            self.on_stop_callback()

    def _on_close(self):
        """Handle window close attempt"""
        # Minimize instead of closing
        self.window.iconify()

    def show(self):
        """Show the window"""
        self.window.deiconify()
        self.window.lift()

    def hide(self):
        """Hide the window"""
        self.window.withdraw()

    def destroy(self):
        """Destroy the window"""
        self.window.destroy()
