"""
TaSched - Setup Window
Schedule builder and task configuration UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
import uuid

from tasched.core.models import Task, Schedule, Settings, SoundProfile, DisplayOptions
from tasched.services.theme_service import get_theme_service
from tasched.services.resource_service import get_resource_service
from tasched.services.storage_service import get_storage_service
from tasched.constants import *


class TaskDialog:
    """Dialog for creating/editing a task"""

    def __init__(self, parent, task: Optional[Task] = None):
        self.parent = parent
        self.result = None
        self.theme = get_theme_service()
        self.resource = get_resource_service()

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Task" if task is None else "Edit Task")
        self.dialog.geometry("900x650")  # Landscape orientation
        self.dialog.configure(bg=self.theme.background)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Load existing task or create new
        self.task = task if task else Task()

        self._create_widgets()
        self._populate_fields()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create dialog widgets"""
        # Logo header frame
        logo_frame = tk.Frame(self.dialog, bg=self.theme.background, height=70)
        logo_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        logo_frame.pack_propagate(False)

        # WAEC Logo
        logo_path = self.resource.get_image(WAEC_LOGO)
        if logo_path:
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(logo_frame, image=logo_photo, bg=self.theme.background)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 15))
            except Exception as e:
                print(f"Error loading logo: {e}")

        # Title label
        title_label = tk.Label(logo_frame, text="Task Configuration",
                              font=(FONT_FAMILY, 18, 'bold'),
                              bg=self.theme.background, fg=self.theme.accent_1)
        title_label.pack(side=tk.LEFT, anchor='w')

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=self.theme.background, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Task Title
        tk.Label(main_frame, text="Task Title:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=0, column=0, sticky='w', pady=5)

        self.title_entry = tk.Entry(main_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)

        # Duration
        tk.Label(main_frame, text="Duration:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=1, column=0, sticky='w', pady=5)

        duration_frame = tk.Frame(main_frame, bg=self.theme.background)
        duration_frame.grid(row=1, column=1, columnspan=2, sticky='w', pady=5)

        tk.Label(duration_frame, text="Hours:", bg=self.theme.background,
                fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(0, 5))
        self.hours_var = tk.StringVar(value="0")
        tk.Spinbox(duration_frame, from_=0, to=23, textvariable=self.hours_var,
                  width=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=5)

        tk.Label(duration_frame, text="Min:", bg=self.theme.background,
                fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(10, 5))
        self.minutes_var = tk.StringVar(value="5")
        tk.Spinbox(duration_frame, from_=0, to=59, textvariable=self.minutes_var,
                  width=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=5)

        tk.Label(duration_frame, text="Sec:", bg=self.theme.background,
                fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(10, 5))
        self.seconds_var = tk.StringVar(value="0")
        tk.Spinbox(duration_frame, from_=0, to=59, textvariable=self.seconds_var,
                  width=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=5)

        # Warning Points
        tk.Label(main_frame, text="Warning Points (seconds):", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=2, column=0, sticky='w', pady=5)

        self.warnings_entry = tk.Entry(main_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=40)
        self.warnings_entry.grid(row=2, column=1, columnspan=2, sticky='ew', pady=5)

        tk.Label(main_frame, text="(Enter minutes, e.g., 10,5,1 for warnings at 10min, 5min, 1min before)",
                font=(FONT_FAMILY, FONT_SIZE_SMALL), bg=self.theme.background,
                fg=self.theme.footer).grid(row=3, column=1, columnspan=2, sticky='w')

        # Warning Sound
        tk.Label(main_frame, text="Warning Sound:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=4, column=0, sticky='w', pady=5)

        self.warning_sound_var = tk.StringVar()
        sound_files = self.resource.list_sound_names()
        self.warning_combo = ttk.Combobox(main_frame, textvariable=self.warning_sound_var,
                                         values=sound_files, state='readonly', width=37)
        self.warning_combo.grid(row=4, column=1, columnspan=2, sticky='ew', pady=5)

        # Time-Up Sound
        tk.Label(main_frame, text="Time-Up Sound:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=5, column=0, sticky='w', pady=5)

        self.timeup_sound_var = tk.StringVar()
        self.timeup_combo = ttk.Combobox(main_frame, textvariable=self.timeup_sound_var,
                                        values=sound_files, state='readonly', width=37)
        self.timeup_combo.grid(row=5, column=1, columnspan=2, sticky='ew', pady=5)

        # Browse button for custom sounds
        tk.Button(main_frame, text="📂 Browse for Custom Sound...",
                 command=self._browse_sound,
                 font=(FONT_FAMILY, FONT_SIZE_SMALL),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=15, pady=5).grid(row=6, column=1, sticky='w', pady=10)

        # Fullscreen Time-up
        self.fullscreen_var = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text="Fullscreen Time-Up Alert", variable=self.fullscreen_var,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                      fg=self.theme.primary_text, selectcolor=self.theme.background,
                      activebackground=self.theme.background).grid(row=7, column=1, sticky='w', pady=10)

        # Ticker Settings
        tk.Label(main_frame, text="Ticker Settings:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=8, column=0, sticky='w', pady=5)

        self.ticker_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(main_frame, text="Enable Ticker", variable=self.ticker_enabled_var,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                      fg=self.theme.primary_text, selectcolor=self.theme.background,
                      activebackground=self.theme.background,
                      command=self._update_ticker_preview).grid(row=8, column=1, sticky='w', pady=5)

        # Ticker Content Selection
        tk.Label(main_frame, text="Show in Ticker:",
                font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                bg=self.theme.background, fg=self.theme.primary_text).grid(row=9, column=0, sticky='w', pady=5)

        ticker_content_frame = tk.Frame(main_frame, bg=self.theme.background)
        ticker_content_frame.grid(row=9, column=1, columnspan=2, sticky='w', pady=5)

        self.ticker_show_task_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ticker_content_frame, text="✓ Current Task Name",
                      variable=self.ticker_show_task_var,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                      fg=self.theme.primary_text, selectcolor=self.theme.background,
                      activebackground=self.theme.background,
                      command=self._update_ticker_preview).pack(side=tk.LEFT, padx=(0, 15))

        self.ticker_show_time_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ticker_content_frame, text="⏱ Time Remaining",
                      variable=self.ticker_show_time_var,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                      fg=self.theme.primary_text, selectcolor=self.theme.background,
                      activebackground=self.theme.background,
                      command=self._update_ticker_preview).pack(side=tk.LEFT, padx=(0, 15))

        self.ticker_show_next_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ticker_content_frame, text="➡ Next Task",
                      variable=self.ticker_show_next_var,
                      font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                      fg=self.theme.primary_text, selectcolor=self.theme.background,
                      activebackground=self.theme.background,
                      command=self._update_ticker_preview).pack(side=tk.LEFT)

        # Preview Label
        tk.Label(main_frame, text="Preview:",
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                bg=self.theme.background, fg=self.theme.footer).grid(row=10, column=0, sticky='w', pady=5)

        self.ticker_preview_label = tk.Label(main_frame, text="",
                font=(FONT_FAMILY, FONT_SIZE_SMALL, 'italic'),
                bg=self.theme.background, fg=self.theme.accent_3,
                wraplength=500, justify=tk.LEFT)
        self.ticker_preview_label.grid(row=10, column=1, columnspan=2, sticky='w', pady=5)

        # Ticker Configuration
        config_frame = tk.Frame(main_frame, bg=self.theme.background)
        config_frame.grid(row=11, column=1, columnspan=2, sticky='w', pady=10)

        tk.Label(config_frame, text="Position:",
                bg=self.theme.background, fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(0,5))
        self.ticker_position_var = tk.StringVar(value="bottom")
        ttk.Combobox(config_frame, textvariable=self.ticker_position_var,
                    values=["top", "bottom"], state='readonly', width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(config_frame, text="Direction:",
                bg=self.theme.background, fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(10,5))
        self.ticker_direction_var = tk.StringVar(value="left")
        ttk.Combobox(config_frame, textvariable=self.ticker_direction_var,
                    values=["left", "right"], state='readonly', width=10).pack(side=tk.LEFT, padx=5)

        tk.Label(config_frame, text="Speed:",
                bg=self.theme.background, fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(10,5))
        self.ticker_speed_var = tk.StringVar(value="medium")
        ttk.Combobox(config_frame, textvariable=self.ticker_speed_var,
                    values=["slow", "medium", "fast"], state='readonly', width=10).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.theme.background)
        button_frame.grid(row=12, column=0, columnspan=3, pady=20)

        tk.Button(button_frame, text="Save", command=self._save,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=30, pady=10, width=10).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_2, fg=self.theme.primary_text,
                 padx=30, pady=10, width=10).pack(side=tk.LEFT, padx=10)

        main_frame.columnconfigure(1, weight=1)

    def _populate_fields(self):
        """Populate fields with existing task data"""
        self.title_entry.insert(0, self.task.title)

        # Duration
        hours, minutes, seconds = self.task.duration_seconds // 3600, \
                                 (self.task.duration_seconds % 3600) // 60, \
                                 self.task.duration_seconds % 60
        self.hours_var.set(str(hours))
        self.minutes_var.set(str(minutes))
        self.seconds_var.set(str(seconds))

        # Warning points
        # Convert seconds to minutes for display
        warnings_str = ','.join([str(w // 60) for w in self.task.warning_points_seconds])
        self.warnings_entry.insert(0, warnings_str)

        # Sounds
        sound_files = self.resource.list_sound_names()

        if self.task.sound_profile.warning_sound:
            if self.task.sound_profile.warning_sound in sound_files:
                self.warning_sound_var.set(self.task.sound_profile.warning_sound)
            elif sound_files:
                self.warning_sound_var.set(sound_files[0])

        if self.task.sound_profile.timeup_sound:
            if self.task.sound_profile.timeup_sound in sound_files:
                self.timeup_sound_var.set(self.task.sound_profile.timeup_sound)
            elif sound_files:
                self.timeup_sound_var.set(sound_files[0])

        # Display options
        self.fullscreen_var.set(self.task.display.fullscreen_timeup)
        self.ticker_enabled_var.set(self.task.display.ticker_enabled)

        # Ticker configuration
        if self.task.display.ticker_text:
            # Parse existing ticker text to set checkboxes
            self._parse_ticker_text(self.task.display.ticker_text)

        self.ticker_position_var.set(self.task.display.ticker_position)
        self.ticker_direction_var.set(self.task.display.ticker_direction)

        # Map speed from int to string
        speed_reverse_map = {1: "slow", 3: "medium", 6: "fast"}
        self.ticker_speed_var.set(speed_reverse_map.get(self.task.display.ticker_speed, "medium"))

        # Update preview
        self._update_ticker_preview()

    def _save(self):
        """Save task"""
        # Validate title
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a task title")
            return

        # Calculate duration
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            total_seconds = hours * 3600 + minutes * 60 + seconds

            if total_seconds == 0:
                messagebox.showerror("Error", "Duration must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid duration values")
            return

        # Parse warning points
        warnings_str = self.warnings_entry.get().strip()
        if warnings_str:
            try:
                # Convert minutes to seconds
                warning_points = [int(x.strip()) * 60 for x in warnings_str.split(',') if x.strip()]
            except ValueError:
                messagebox.showerror("Error", "Invalid warning points format")
                return
        else:
            warning_points = []

        # Update task
        self.task.title = title
        self.task.duration_seconds = total_seconds
        self.task.remaining_seconds = total_seconds
        self.task.warning_points_seconds = warning_points

        # Sound profile
        warning_sound = self.warning_sound_var.get()
        timeup_sound = self.timeup_sound_var.get()

        if warning_sound:
            self.task.sound_profile.warning_sound = warning_sound
        if timeup_sound:
            self.task.sound_profile.timeup_sound = timeup_sound

        # Display options
        self.task.display.fullscreen_timeup = self.fullscreen_var.get()
        self.task.display.ticker_enabled = self.ticker_enabled_var.get()

        # Build ticker text from selected options
        self.task.display.ticker_text = self._build_ticker_text()
        self.task.display.ticker_position = self.ticker_position_var.get()
        self.task.display.ticker_direction = self.ticker_direction_var.get()

        # Map speed string to int
        speed_map = {"slow": 1, "medium": 3, "fast": 6}
        self.task.display.ticker_speed = speed_map.get(self.ticker_speed_var.get(), 3)

        self.result = self.task
        self.dialog.destroy()

    def _browse_sound(self):
        """Browse for custom sound file"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Alert Sound",
            filetypes=filetypes
        )

        if filename:
            import shutil
            import os

            # Copy to sounds directory
            dest_name = os.path.basename(filename)
            sounds_dir = self.resource.sounds_path
            dest_path = sounds_dir / dest_name

            try:
                shutil.copy(filename, dest_path)

                # Refresh combos and select new file
                sound_files = self.resource.list_sound_names()

                # Update both warning and timeup combos
                self.warning_combo['values'] = sound_files
                self.warning_sound_var.set(dest_name)

                self.timeup_combo['values'] = sound_files
                self.timeup_sound_var.set(dest_name)

                messagebox.showinfo("Success", f"Sound '{dest_name}' added successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy sound file: {e}")

    def _build_ticker_text(self) -> str:
        """Build ticker message from checkbox selections"""
        parts = []

        if self.ticker_show_task_var.get():
            parts.append("[TASK_NAME]")

        if self.ticker_show_time_var.get():
            parts.append("[TIME_REMAINING]")

        if self.ticker_show_next_var.get():
            parts.append("Next: [NEXT_TASK]")

        if not parts:
            return "Current Task: [TASK_NAME]"  # Default fallback

        # Join with separator
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} - {parts[1]}"
        else:
            return f"{parts[0]} - {parts[1]} | {parts[2]}"

    def _parse_ticker_text(self, text: str):
        """Parse ticker text and set checkboxes accordingly"""
        self.ticker_show_task_var.set("[TASK_NAME]" in text)
        self.ticker_show_time_var.set("[TIME_REMAINING]" in text)
        self.ticker_show_next_var.set("[NEXT_TASK]" in text)

    def _update_ticker_preview(self):
        """Update the ticker preview label with example text"""
        if not self.ticker_enabled_var.get():
            self.ticker_preview_label.config(text="(Ticker is disabled)")
            return

        # Build preview with example values
        preview = self._build_ticker_text()

        # Replace placeholders with example values
        preview = preview.replace("[TASK_NAME]", "Mathematics")
        preview = preview.replace("[TIME_REMAINING]", "15:30")
        preview = preview.replace("[NEXT_TASK]", "English Language")

        if not preview or preview == "":
            preview = "(Select at least one option above)"

        self.ticker_preview_label.config(text=f"Example: {preview}")

    def show(self) -> Optional[Task]:
        """Show dialog and return task"""
        self.dialog.wait_window()
        return self.result


class SetupWindow(tk.Frame):
    """Setup window for schedule creation"""

    def __init__(self, parent, on_start_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_start_callback = on_start_callback

        self.theme = get_theme_service()
        self.storage = get_storage_service()
        self.resource = get_resource_service()

        self.current_schedule = Schedule(name="New Schedule")

        self.configure(bg=self.theme.background)
        self._create_widgets()

    def _create_widgets(self):
        """Create setup UI widgets"""
        # Header with logo
        header_frame = tk.Frame(self, bg=self.theme.background, height=100)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        header_frame.pack_propagate(False)

        # WAEC Logo on the left
        logo_path = self.resource.get_image(WAEC_LOGO)
        if logo_path:
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((80, 80), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                logo_label = tk.Label(header_frame, image=logo_photo, bg=self.theme.background)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 20))
            except Exception as e:
                print(f"Error loading logo: {e}")

        # Text labels on the right
        text_frame = tk.Frame(header_frame, bg=self.theme.background)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(text_frame, text="Schedule Builder",
                font=(FONT_FAMILY, 24, 'bold'), bg=self.theme.background,
                fg=self.theme.accent_1).pack(anchor='w')

        tk.Label(text_frame, text="Create and configure your task schedule",
                font=(FONT_FAMILY, FONT_SIZE_NORMAL), bg=self.theme.background,
                fg=self.theme.primary_text).pack(anchor='w')

        # Schedule Name
        name_frame = tk.Frame(self, bg=self.theme.background)
        name_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(name_frame, text="Schedule Name:",
                font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).pack(side=tk.LEFT, padx=(0, 10))

        self.schedule_name_var = tk.StringVar(value="New Schedule")
        self.schedule_name_entry = tk.Entry(name_frame, textvariable=self.schedule_name_var,
                                            font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=40)
        self.schedule_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Task List
        list_frame = tk.Frame(self, bg=self.theme.background)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(list_frame, text="Tasks:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).pack(anchor='w', pady=(0, 5))

        # Treeview for tasks
        columns = ('Title', 'Duration', 'Warnings')
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)

        self.task_tree.heading('#0', text='#')
        self.task_tree.heading('Title', text='Task Title')
        self.task_tree.heading('Duration', text='Duration')
        self.task_tree.heading('Warnings', text='Warnings')

        self.task_tree.column('#0', width=40)
        self.task_tree.column('Title', width=300)
        self.task_tree.column('Duration', width=100)
        self.task_tree.column('Warnings', width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Task Control Buttons
        task_buttons_frame = tk.Frame(self, bg=self.theme.background)
        task_buttons_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(task_buttons_frame, text="➕ Add Task", command=self._add_task,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(task_buttons_frame, text="✏ Edit Task", command=self._edit_task,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(task_buttons_frame, text="🗑 Remove Task", command=self._remove_task,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_2, fg=self.theme.primary_text,
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(task_buttons_frame, text="⬆ Move Up", command=self._move_up,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                 bg=self.theme.background, fg=self.theme.primary_text,
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(task_buttons_frame, text="⬇ Move Down", command=self._move_down,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                 bg=self.theme.background, fg=self.theme.primary_text,
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)

        # Schedule Actions
        action_frame = tk.Frame(self, bg=self.theme.background)
        action_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Button(action_frame, text="💾 Save Schedule", command=self._save_schedule,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_3, fg=self.theme.background,
                 padx=20, pady=12).pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="📂 Load Schedule", command=self._load_schedule,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=20, pady=12).pack(side=tk.LEFT, padx=5)

        tk.Button(action_frame, text="▶ Start Schedule", command=self._start_schedule,
                 font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=30, pady=12).pack(side=tk.RIGHT, padx=5)

    def _add_task(self):
        """Add new task"""
        dialog = TaskDialog(self.parent)
        task = dialog.show()

        if task:
            self.current_schedule.add_task(task)
            self._refresh_task_list()

    def _edit_task(self):
        """Edit selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return

        item = selection[0]
        index = self.task_tree.index(item)

        task = self.current_schedule.tasks[index]
        dialog = TaskDialog(self.parent, task)
        updated_task = dialog.show()

        if updated_task:
            self.current_schedule.tasks[index] = updated_task
            self._refresh_task_list()

    def _remove_task(self):
        """Remove selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to remove")
            return

        if messagebox.askyesno("Confirm", "Remove this task?"):
            item = selection[0]
            index = self.task_tree.index(item)
            self.current_schedule.tasks.pop(index)
            self.current_schedule.task_ids.pop(index)
            self._refresh_task_list()

    def _move_up(self):
        """Move task up in order"""
        selection = self.task_tree.selection()
        if not selection:
            return

        item = selection[0]
        index = self.task_tree.index(item)

        if index > 0:
            self.current_schedule.reorder_tasks(index, index - 1)
            self._refresh_task_list()
            # Reselect moved item
            new_item = self.task_tree.get_children()[index - 1]
            self.task_tree.selection_set(new_item)

    def _move_down(self):
        """Move task down in order"""
        selection = self.task_tree.selection()
        if not selection:
            return

        item = selection[0]
        index = self.task_tree.index(item)

        if index < len(self.current_schedule.tasks) - 1:
            self.current_schedule.reorder_tasks(index, index + 1)
            self._refresh_task_list()
            # Reselect moved item
            new_item = self.task_tree.get_children()[index + 1]
            self.task_tree.selection_set(new_item)

    def _refresh_task_list(self):
        """Refresh task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Add tasks
        for i, task in enumerate(self.current_schedule.tasks):
            duration_str = f"{task.duration_seconds // 3600}h {(task.duration_seconds % 3600) // 60}m {task.duration_seconds % 60}s"
            # Display warnings in minutes (converted from seconds)
            warnings_str = ', '.join([f"{w // 60}min" for w in task.warning_points_seconds[:3] if w > 0])

            self.task_tree.insert('', 'end', text=f"{i+1}",
                                 values=(task.title, duration_str, warnings_str))

    def _save_schedule(self):
        """Save current schedule"""
        if not self.current_schedule.tasks:
            messagebox.showwarning("No Tasks", "Add at least one task before saving")
            return

        self.current_schedule.name = self.schedule_name_var.get()
        self.storage.save_schedule(self.current_schedule)
        messagebox.showinfo("Saved", f"Schedule '{self.current_schedule.name}' saved successfully!")

    def _load_schedule(self):
        """Load existing schedule"""
        schedules = self.storage.get_all_schedules()

        if not schedules:
            messagebox.showinfo("No Schedules", "No saved schedules found")
            return

        # Simple selection dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Load Schedule")
        dialog.geometry("500x400")
        dialog.configure(bg=self.theme.background)

        tk.Label(dialog, text="Select a schedule to load:",
                font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                bg=self.theme.background, fg=self.theme.primary_text).pack(pady=10)

        listbox = tk.Listbox(dialog, font=(FONT_FAMILY, FONT_SIZE_NORMAL), height=12)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for schedule in schedules:
            listbox.insert(tk.END, f"{schedule.name} ({len(schedule.tasks)} tasks)")

        def load_selected():
            selection = listbox.curselection()
            if selection:
                selected_schedule = schedules[selection[0]]
                self.current_schedule = selected_schedule
                self.schedule_name_var.set(selected_schedule.name)
                self._refresh_task_list()
                dialog.destroy()

        # Double-click to load
        listbox.bind('<Double-Button-1>', lambda e: load_selected())

        # Button frame
        btn_frame = tk.Frame(dialog, bg=self.theme.background)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", command=load_selected,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
                 bg=self.theme.accent_1, fg=self.theme.background,
                 padx=20, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                 bg=self.theme.accent_2, fg=self.theme.primary_text,
                 padx=20, pady=8).pack(side=tk.LEFT, padx=5)

    def _start_schedule(self):
        """Start the current schedule"""
        if not self.current_schedule.tasks:
            messagebox.showwarning("No Tasks", "Add at least one task before starting")
            return

        self.current_schedule.name = self.schedule_name_var.get()

        if self.on_start_callback:
            self.on_start_callback(self.current_schedule)
