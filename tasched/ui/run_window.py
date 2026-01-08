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
                 on_skip_callback=None, on_stop_callback=None, on_force_next_callback=None):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.theme = get_theme_service()
        self.resource = get_resource_service()
        self.time_service = TimeService()

        # Callbacks
        self.on_pause_callback = on_pause_callback
        self.on_resume_callback = on_resume_callback
        self.on_skip_callback = on_skip_callback
        self.on_force_next_callback = on_force_next_callback if on_force_next_callback else on_skip_callback
        self.on_stop_callback = on_stop_callback

        # State
        self.is_paused = False
        self.is_fullscreen = True
        self.current_task = None
        self.next_task = None
        self.schedule = None

        # Ticker state
        self.ticker_offset = 0
        self.ticker_enabled = False

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
        self.window.bind('p', lambda e: self.toggle_pause())  # P for Pause
        self.window.bind('P', lambda e: self.toggle_pause())
        self.window.bind('m', lambda e: self.toggle_mute())  # M for Mute
        self.window.bind('M', lambda e: self.toggle_mute())
        self.window.bind('s', lambda e: self._on_skip())  # S for Skip
        self.window.bind('S', lambda e: self._on_skip())
        self.window.bind('n', lambda e: self._on_force_next())  # N for Next
        self.window.bind('N', lambda e: self._on_force_next())
        self.window.bind('x', lambda e: self._on_stop())  # X for Stop (eXit)
        self.window.bind('X', lambda e: self._on_stop())

        # Protocol for window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        """Create UI widgets"""
        # Main container
        main_frame = tk.Frame(self.window, bg=self.theme.background)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar (logo, schedule name and clock)
        top_frame = tk.Frame(main_frame, bg=self.theme.background, height=80)
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        top_frame.pack_propagate(False)

        # WAEC Logo on the left
        logo_path = self.resource.get_image(WAEC_LOGO)
        if logo_path:
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(top_frame, image=logo_photo, bg=self.theme.background)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 15))
            except Exception as e:
                print(f"Error loading logo: {e}")

        self.schedule_label = tk.Label(
            top_frame,
            text="",
            font=(FONT_FAMILY, 32, 'bold'),  # Increased from FONT_SIZE_LARGE (18) to 32
            bg=self.theme.background,
            fg=self.theme.accent_1
        )
        self.schedule_label.pack(side=tk.LEFT, padx=(0, 20))

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
            font=(FONT_FAMILY, 48, 'bold'),  # Increased from 32 to 48
            bg=self.theme.background,
            fg=self.theme.primary_text,
            wraplength=1000,  # Allow text wrapping
            justify=tk.CENTER
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
            text="⏸ Pause (P)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self.toggle_pause,
            **self.theme.get_button_style(),
            width=14
        )
        self.pause_button.pack(side=tk.LEFT, padx=10)

        # Mute toggle button
        self.is_muted = False
        self.mute_button = tk.Button(
            button_frame,
            text="🔇 Mute (M)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self.toggle_mute,
            **self.theme.get_button_style(),
            width=14
        )
        self.mute_button.pack(side=tk.LEFT, padx=10)

        skip_button = tk.Button(
            button_frame,
            text="⏭ Skip (S)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self._on_skip,
            **self.theme.get_button_style(),
            width=14
        )
        skip_button.pack(side=tk.LEFT, padx=10)

        # Next Task button (forces immediate start, adjusts remaining times)
        next_button = tk.Button(
            button_frame,
            text="⏭ Next (N)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self._on_force_next,  # Different from skip
            **self.theme.get_button_style(),
            width=14
        )
        next_button.pack(side=tk.LEFT, padx=10)

        stop_button = tk.Button(
            button_frame,
            text="⏹ Stop (X)",
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
            width=14
        )
        stop_button.pack(side=tk.LEFT, padx=10)

        # Footer bar (pack first so it's at the bottom)
        footer_frame = tk.Frame(main_frame, bg=self.theme.background, height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(5, 10))
        footer_frame.pack_propagate(False)

        # Ticker (scrolling message bar) - pack after footer so it's above it
        self.ticker_frame = tk.Frame(main_frame, bg=self.theme.accent_1, height=50)
        self.ticker_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.ticker_frame.pack_propagate(False)

        self.ticker_canvas = tk.Canvas(self.ticker_frame, bg=self.theme.accent_1,
                                       highlightthickness=0, height=50)
        self.ticker_canvas.pack(fill=tk.BOTH, expand=True)

        self.ticker_text_id = None
        self.ticker_message = ""

        # Help text on left
        help_text = "P: Pause | M: Mute | S: Skip | N: Next | X: Stop | F11: Fullscreen | ESC: Exit Fullscreen"
        help_label = tk.Label(
            footer_frame,
            text=help_text,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            bg=self.theme.background,
            fg=self.theme.footer
        )
        help_label.pack(side=tk.LEFT)

        # Powered By text on right
        powered_by_label = tk.Label(
            footer_frame,
            text="Powered By",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, 'italic'),
            bg=self.theme.background,
            fg='white'
        )
        powered_by_label.pack(side=tk.RIGHT, padx=(0, 5))

        waec_label = tk.Label(
            footer_frame,
            text="WAEC - Psychometrics Dept.",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, 'bold'),
            bg=self.theme.background,
            fg='white'
        )
        waec_label.pack(side=tk.RIGHT)

        # Update clock periodically
        self._update_clock()

    def update(self, schedule: Schedule, current_task: Task, next_task: Optional[Task] = None):
        """Update display with current schedule state"""
        # Store references
        self.current_task = current_task
        self.next_task = next_task
        self.schedule = schedule

        # Update schedule name
        self.schedule_label.config(text=schedule.name)

        # Update task title with optional prefix
        task_prefix = getattr(schedule, 'task_prefix', 'Now')  # Default to 'Now'
        if task_prefix:
            title_text = f"{task_prefix}: {current_task.title}"
        else:
            title_text = current_task.title
        self.task_title_label.config(text=title_text)

        # Update countdown
        remaining = current_task.remaining_seconds
        countdown_text = self.time_service.format_seconds(remaining)
        self.countdown_label.config(text=countdown_text)

        # Update status
        status_text = self.time_service.get_friendly_time_remaining(remaining)
        self.status_label.config(text=status_text)

        # Update next task info with start time if available
        if next_task:
            duration_str = self.time_service.format_duration(next_task.duration_seconds, short=True)

            # Add start time if task has absolute_start_time
            if hasattr(next_task, 'absolute_start_time') and next_task.absolute_start_time:
                # Convert 24-hour to 12-hour format for display
                try:
                    hour, minute = map(int, next_task.absolute_start_time.split(':'))
                    ampm = 'am' if hour < 12 else 'pm'
                    display_hour = hour if hour <= 12 else hour - 12
                    if display_hour == 0:
                        display_hour = 12
                    time_str = f"{display_hour}:{minute:02d}{ampm}"
                    next_text = f"Next: {next_task.title} ({duration_str}, starts at {time_str})"
                except:
                    next_text = f"Next: {next_task.title} ({duration_str})"
            else:
                next_text = f"Next: {next_task.title} ({duration_str})"

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

        # Update ticker if enabled
        if current_task.display.ticker_enabled:
            self._update_ticker()

    def _update_clock(self):
        """Update the clock display"""
        current_time = self.time_service.get_current_time()
        self.clock_label.config(text=current_time)
        self.window.after(1000, self._update_clock)

    def toggle_pause(self):
        """Toggle pause/resume"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_button.config(text="▶ Resume (P)")
            if self.on_pause_callback:
                self.on_pause_callback()
        else:
            self.pause_button.config(text="⏸ Pause (P)")
            if self.on_resume_callback:
                self.on_resume_callback()

    def toggle_mute(self):
        """Toggle audio mute"""
        from tasched.services.audio_service import get_audio_service
        audio = get_audio_service()

        self.is_muted = not self.is_muted

        if self.is_muted:
            audio.disable()
            self.mute_button.config(text="🔊 Unmute (M)")
        else:
            audio.enable()
            self.mute_button.config(text="🔇 Mute (M)")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)

    def _on_skip(self):
        """Handle skip button (waits for next task's absolute time)"""
        if self.on_skip_callback:
            self.on_skip_callback()

    def _on_force_next(self):
        """Handle next task button (forces immediate start, adjusts times)"""
        if self.on_force_next_callback:
            self.on_force_next_callback()

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

    def _update_ticker(self):
        """Update ticker message and animate"""
        if not self.current_task or not self.current_task.display.ticker_enabled:
            # Hide ticker if not enabled
            self.ticker_frame.pack_forget()
            return

        # Show ticker frame
        self.ticker_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Build ticker message from placeholders
        ticker_text = self.current_task.display.ticker_text
        if not ticker_text:
            return

        # Replace placeholders
        message = ticker_text.replace("[TASK_NAME]", self.current_task.title)

        if "[TIME_REMAINING]" in message:
            time_remaining = self.time_service.format_seconds(self.current_task.remaining_seconds)
            message = message.replace("[TIME_REMAINING]", time_remaining)

        if "[NEXT_TASK]" in message and self.next_task:
            message = message.replace("[NEXT_TASK]", self.next_task.title)
        elif "[NEXT_TASK]" in message:
            message = message.replace("Next: [NEXT_TASK]", "Last Task")
            message = message.replace("[NEXT_TASK]", "None")

        # Only update if message changed
        if message != self.ticker_message:
            self.ticker_message = message
            self.ticker_offset = 0
            if self.ticker_text_id:
                self.ticker_canvas.delete(self.ticker_text_id)

            # Create scrolling text
            self.ticker_text_id = self.ticker_canvas.create_text(
                self.ticker_canvas.winfo_width(),
                25,
                text=self.ticker_message,
                font=(FONT_FAMILY, 18, 'bold'),
                fill='white',
                anchor='w'
            )

        # Animate ticker
        self._animate_ticker()

    def _animate_ticker(self):
        """Animate ticker scrolling"""
        if not self.current_task or not self.current_task.display.ticker_enabled:
            return

        if not self.ticker_text_id:
            return

        # Get speed from current task display options
        speed = self.current_task.display.ticker_speed
        direction = self.current_task.display.ticker_direction

        # Move text
        if direction == "left":
            self.ticker_canvas.move(self.ticker_text_id, -speed, 0)
        else:
            self.ticker_canvas.move(self.ticker_text_id, speed, 0)

        # Get current position
        coords = self.ticker_canvas.coords(self.ticker_text_id)
        if not coords:
            return

        x_pos = coords[0]

        # Reset position if scrolled off screen
        canvas_width = self.ticker_canvas.winfo_width()
        bbox = self.ticker_canvas.bbox(self.ticker_text_id)

        if bbox:
            text_width = bbox[2] - bbox[0]

            if direction == "left":
                # Reset to right side when fully scrolled off left
                if x_pos + text_width < 0:
                    self.ticker_canvas.coords(self.ticker_text_id, canvas_width, 25)
            else:
                # Reset to left side when fully scrolled off right
                if x_pos > canvas_width:
                    self.ticker_canvas.coords(self.ticker_text_id, -text_width, 25)

        # Continue animation (100ms delay for smoother, slower scrolling)
        self.ticker_canvas.after(100, self._animate_ticker)
