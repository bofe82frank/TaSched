"""
TaSched - Alert Windows
Warning popup and Time-Up windows
"""

import tkinter as tk
from PIL import Image, ImageTk

from tasched.core.models import Task
from tasched.core.time_service import TimeService
from tasched.services.theme_service import get_theme_service
from tasched.services.resource_service import get_resource_service
from tasched.services.audio_service import get_audio_service
from tasched.constants import *


class WarningPopup:
    """Warning popup shown at threshold points"""

    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.window = None
        self.theme = get_theme_service()
        self.time_service = TimeService()
        self.audio = get_audio_service()
        self.auto_dismiss_id = None

    def show(self, task: Task, remaining_seconds: int, next_task_title: str = None):
        """Show warning popup"""
        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title("Warning")
        self.window.geometry(f"{WARNING_POPUP_WIDTH}x{WARNING_POPUP_HEIGHT}")
        self.window.configure(bg=self.theme.accent_2)  # Warning color

        # Center on screen
        self._center_window()

        # Always on top
        self.window.attributes('-topmost', True)

        # Main frame
        main_frame = tk.Frame(self.window, bg=self.theme.accent_2, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Warning icon/title
        warning_label = tk.Label(
            main_frame,
            text="⚠ WARNING",
            font=(FONT_FAMILY, FONT_SIZE_XLARGE, 'bold'),
            bg=self.theme.accent_2,
            fg=self.theme.primary_text
        )
        warning_label.pack(pady=(10, 20))

        # Task name
        task_label = tk.Label(
            main_frame,
            text=task.title,
            font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
            bg=self.theme.accent_2,
            fg=self.theme.primary_text,
            wraplength=350
        )
        task_label.pack(pady=10)

        # Time remaining
        time_text = self.time_service.get_friendly_time_remaining(remaining_seconds)
        time_label = tk.Label(
            main_frame,
            text=time_text,
            font=(FONT_FAMILY, FONT_SIZE_XLARGE),
            bg=self.theme.accent_2,
            fg=self.theme.primary_text
        )
        time_label.pack(pady=10)

        # Next task info
        if next_task_title:
            next_label = tk.Label(
                main_frame,
                text=f"Next: {next_task_title}",
                font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                bg=self.theme.accent_2,
                fg=self.theme.primary_text
            )
            next_label.pack(pady=5)

        # OK button
        ok_button = tk.Button(
            main_frame,
            text="OK",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
            command=self.dismiss,
            bg=self.theme.primary_text,
            fg=self.theme.accent_2,
            relief='flat',
            bd=0,
            padx=30,
            pady=10
        )
        ok_button.pack(pady=20)

        # Bind Enter/Escape to dismiss
        self.window.bind('<Return>', lambda e: self.dismiss())
        self.window.bind('<Escape>', lambda e: self.dismiss())

        # Play warning sound
        resource = get_resource_service()
        sound_path = resource.get_sound(task.sound_profile.warning_sound)
        if sound_path:
            self.audio.play_warning_sound(sound_path)

        # Auto-dismiss after configured time
        self.auto_dismiss_id = self.window.after(DEFAULT_WARNING_AUTO_DISMISS * 1000, self.dismiss)

    def _center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def dismiss(self):
        """Dismiss the popup"""
        if self.auto_dismiss_id:
            try:
                self.window.after_cancel(self.auto_dismiss_id)
            except Exception:
                pass

        if self.window:
            self.window.destroy()
            self.window = None


class TimeUpWindow:
    """Time-up alert window (fullscreen or popup)"""

    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.window = None
        self.theme = get_theme_service()
        self.resource = get_resource_service()
        self.audio = get_audio_service()
        self.auto_close_id = None

    def show(self, task: Task, fullscreen: bool = True, next_task_title: str = None):
        """Show time-up window"""
        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title("Time's Up!")

        if fullscreen:
            self.window.attributes('-fullscreen', True)
        else:
            self.window.geometry(f"{TIMEUP_WINDOW_WIDTH}x{TIMEUP_WINDOW_HEIGHT}")
            self._center_window()

        self.window.configure(bg=self.theme.background)
        self.window.attributes('-topmost', True)

        # Try to load background image
        bg_image_path = self.resource.get_image(WAEC_BACKGROUND)
        if bg_image_path:
            try:
                # Load and display background image
                self._create_background(bg_image_path)
            except Exception as e:
                print(f"Error loading background: {e}")
                self._create_solid_background()
        else:
            self._create_solid_background()

        # Main frame (overlay on background)
        main_frame = tk.Frame(self.window, bg=self.theme.background)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logo (if available)
        logo_path = self.resource.get_image(WAEC_LOGO)
        if logo_path:
            try:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(main_frame, image=logo_photo, bg=self.theme.background)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(pady=20)
            except Exception:
                pass

        # Time's up message
        timeup_label = tk.Label(
            main_frame,
            text="⏰ TIME'S UP!",
            font=(FONT_FAMILY, 64, 'bold'),
            bg=self.theme.background,
            fg=self.theme.accent_3
        )
        timeup_label.pack(pady=20)

        # Task name
        task_label = tk.Label(
            main_frame,
            text=task.title,
            font=(FONT_FAMILY, FONT_SIZE_TITLE, 'bold'),
            bg=self.theme.background,
            fg=self.theme.primary_text,
            wraplength=700
        )
        task_label.pack(pady=20)

        # Next task info
        if next_task_title:
            next_frame = tk.Frame(main_frame, bg=self.theme.accent_1, padx=30, pady=15)
            next_frame.pack(pady=30)

            next_label = tk.Label(
                next_frame,
                text=f"Next Task: {next_task_title}",
                font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
                bg=self.theme.accent_1,
                fg=self.theme.background
            )
            next_label.pack()

        # Dismiss button
        dismiss_button = tk.Button(
            main_frame,
            text="Continue",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
            command=self.dismiss,
            bg=self.theme.accent_1,
            fg=self.theme.background,
            activebackground=self.theme.accent_3,
            activeforeground=self.theme.background,
            relief='flat',
            bd=0,
            padx=50,
            pady=15
        )
        dismiss_button.pack(pady=30)

        # Help text
        help_label = tk.Label(
            main_frame,
            text="Press ENTER or ESC to continue",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            bg=self.theme.background,
            fg=self.theme.footer
        )
        help_label.pack(pady=10)

        # Bind keys
        self.window.bind('<Return>', lambda e: self.dismiss())
        self.window.bind('<Escape>', lambda e: self.dismiss())

        # Play time-up sound
        sound_path = self.resource.get_sound(task.sound_profile.timeup_sound)
        if sound_path:
            self.audio.play_timeup_sound(sound_path)

        # Auto-close after configured time
        self.auto_close_id = self.window.after(DEFAULT_TIMEUP_AUTO_CLOSE * 1000, self.dismiss)

    def _create_background(self, image_path: str):
        """Create background with image"""
        try:
            img = Image.open(image_path)
            # Get screen size
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            # Resize image to screen size
            img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(img)

            bg_label = tk.Label(self.window, image=bg_photo)
            bg_label.image = bg_photo  # Keep reference
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error creating background: {e}")
            self._create_solid_background()

    def _create_solid_background(self):
        """Create solid color background"""
        canvas = tk.Canvas(self.window, bg=self.theme.background, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def _center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def dismiss(self):
        """Dismiss the window"""
        if self.auto_close_id:
            try:
                self.window.after_cancel(self.auto_close_id)
            except Exception:
                pass

        if self.window:
            self.window.destroy()
            self.window = None
