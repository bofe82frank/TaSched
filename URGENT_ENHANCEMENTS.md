# TaSched - Urgent UI/UX Enhancements

## ✅ COMPLETED
1. **Setup window fullscreen at launch** - DONE
2. **Task dialog landscape (900x650)** - DONE
3. **Warning points in minutes** - DONE
4. **Digital clock enhanced** - DONE
5. **Footer updated with Psychometric Dept** - DONE

---

## 🚧 REMAINING ENHANCEMENTS

### 3. Next Task Button & Display

**File**: `tasched/ui/run_window.py`

**Add to button frame** (around line 153):
```python
# After skip_button, add Next Task button
next_button = tk.Button(
    button_frame,
    text="⏭ Next Task",
    font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
    command=self._on_skip,  # Same as skip
    **self.theme.get_button_style(),
    width=12
)
next_button.pack(side=tk.LEFT, padx=10)
```

**Optional Next Task Display** - Already implemented in `self.next_task_label`

---

### 4. Increase Task Title Font & Multiline

**File**: `tasched/ui/run_window.py` (line 103-110)

**Current**:
```python
self.task_title_label = tk.Label(
    center_frame,
    text="",
    font=(FONT_FAMILY, FONT_SIZE_TITLE, 'bold'),
    bg=self.theme.background,
    fg=self.theme.primary_text
)
```

**Change to**:
```python
self.task_title_label = tk.Label(
    center_frame,
    text="",
    font=(FONT_FAMILY, 48, 'bold'),  # Increased from 32 to 48
    bg=self.theme.background,
    fg=self.theme.primary_text,
    wraplength=1000,  # Allow text wrapping
    justify=tk.CENTER
)
```

---

### 5. Load Schedule Dialog Improvements

**File**: `tasched/ui/setup_window.py` (around line 480)

**Add OK button and double-click**:
```python
def _load_schedule(self):
    """Load existing schedule"""
    schedules = self.storage.get_all_schedules()

    if not schedules:
        messagebox.showinfo("No Schedules", "No saved schedules found")
        return

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
```

---

### 6. Mute Button on Running Window

**File**: `tasched/ui/run_window.py`

**Add after pause_button** (around line 163):
```python
# Mute toggle button
self.is_muted = False
self.mute_button = tk.Button(
    button_frame,
    text="🔇 Mute",
    font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
    command=self.toggle_mute,
    **self.theme.get_button_style(),
    width=12
)
self.mute_button.pack(side=tk.LEFT, padx=10)
```

**Add method**:
```python
def toggle_mute(self):
    """Toggle audio mute"""
    from tasched.services.audio_service import get_audio_service
    audio = get_audio_service()

    self.is_muted = not self.is_muted

    if self.is_muted:
        audio.disable()
        self.mute_button.config(text="🔊 Unmute")
    else:
        audio.enable()
        self.mute_button.config(text="🔇 Mute")
```

---

### 7. Mute Button on Time-Up Window

**File**: `tasched/ui/alert_windows.py` (TimeUpWindow class)

**Add to button area** (around line 230):
```python
# Mute button
mute_button = tk.Button(
    main_frame,
    text="🔇 Mute",
    font=(FONT_FAMILY, FONT_SIZE_NORMAL),
    command=lambda: self._mute_audio(),
    bg=self.theme.accent_2,
    fg=self.theme.primary_text,
    padx=20,
    pady=10
)
mute_button.pack(pady=10)
```

**Add method**:
```python
def _mute_audio(self):
    """Mute the time-up sound"""
    self.audio.stop()
```

---

### 8. Separate Tone Selection (Warning vs Time-Up)

**File**: `tasched/ui/setup_window.py` (TaskDialog)

**Replace current sound selection** (around line 96-104):
```python
# Warning Sound
tk.Label(main_frame, text="Warning Sound:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=4, column=0, sticky='w', pady=5)

self.warning_sound_var = tk.StringVar()
sound_files = self.resource.list_sound_names()
warning_combo = ttk.Combobox(main_frame, textvariable=self.warning_sound_var,
                             values=sound_files, state='readonly', width=37)
warning_combo.grid(row=4, column=1, columnspan=2, sticky='ew', pady=5)

# Time-Up Sound
tk.Label(main_frame, text="Time-Up Sound:", font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=5, column=0, sticky='w', pady=5)

self.timeup_sound_var = tk.StringVar()
timeup_combo = ttk.Combobox(main_frame, textvariable=self.timeup_sound_var,
                            values=sound_files, state='readonly', width=37)
timeup_combo.grid(row=5, column=1, columnspan=2, sticky='ew', pady=5)

# Browse button for custom sounds
tk.Button(main_frame, text="📂 Browse for Custom Sound...",
         command=self._browse_sound,
         font=(FONT_FAMILY, FONT_SIZE_SMALL),
         bg=self.theme.accent_1, fg=self.theme.background,
         padx=15, pady=5).grid(row=6, column=1, sticky='w', pady=10)
```

**Update populate method**:
```python
# Sounds
if self.task.sound_profile.warning_sound:
    self.warning_sound_var.set(self.task.sound_profile.warning_sound)

if self.task.sound_profile.timeup_sound:
    self.timeup_sound_var.set(self.task.sound_profile.timeup_sound)
```

**Update save method**:
```python
# Sound profile
warning_sound = self.warning_sound_var.get()
timeup_sound = self.timeup_sound_var.get()

if warning_sound:
    self.task.sound_profile.warning_sound = warning_sound
if timeup_sound:
    self.task.sound_profile.timeup_sound = timeup_sound
```

---

### 9. Browse for Custom Sound

**Add method to TaskDialog**:
```python
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
            if hasattr(self, 'warning_combo'):
                self.warning_combo['values'] = sound_files
                self.warning_sound_var.set(dest_name)

            if hasattr(self, 'timeup_combo'):
                self.timeup_combo['values'] = sound_files
                self.timeup_sound_var.set(dest_name)

            messagebox.showinfo("Success", f"Sound '{dest_name}' added successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy sound file: {e}")
```

---

### 10. Ticker Message Configuration

**Add to TaskDialog** (after ticker enable checkbox):
```python
# Ticker Message
tk.Label(main_frame, text="Ticker Message:",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=8, column=0, sticky='w', pady=5)

self.ticker_text_var = tk.StringVar(value="Current Task: [TASK_NAME]")
ticker_entry = tk.Entry(main_frame, textvariable=self.ticker_text_var,
                       font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=50)
ticker_entry.grid(row=8, column=1, columnspan=2, sticky='ew', pady=5)

tk.Label(main_frame, text="Use: [TASK_NAME], [NEXT_TASK], [TIME_REMAINING]",
        font=(FONT_FAMILY, FONT_SIZE_SMALL),
        bg=self.theme.background, fg=self.theme.footer).grid(row=9, column=1, columnspan=2, sticky='w')

# Ticker Configuration
config_frame = tk.Frame(main_frame, bg=self.theme.background)
config_frame.grid(row=10, column=1, columnspan=2, sticky='w', pady=10)

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
```

**Update save method**:
```python
# Ticker settings
self.task.display.ticker_enabled = self.ticker_enabled_var.get()
self.task.display.ticker_text = self.ticker_text_var.get()
self.task.display.ticker_position = self.ticker_position_var.get()
self.task.display.ticker_direction = self.ticker_direction_var.get()

# Map speed
speed_map = {"slow": 1, "medium": 3, "fast": 6}
self.task.display.ticker_speed = speed_map.get(self.ticker_speed_var.get(), 3)
```

---

## PRIORITY ORDER

**IMMEDIATE** (Do First):
1. ✅ Fullscreen setup window
2. ✅ Task dialog landscape
3. Load schedule OK button & double-click
4. Separate warning/timeup sounds
5. Browse for custom sounds

**HIGH PRIORITY**:
6. Mute buttons (running + time-up)
7. Increase task title font & multiline
8. Next Task button

**MEDIUM PRIORITY**:
9. Ticker message configuration UI
10. Ticker overlay implementation

---

## FILES TO MODIFY

1. ✅ `app.py` - Fullscreen
2. ✅ `tasched/ui/setup_window.py` - Dialog size, sounds, browse, ticker, load dialog
3. `tasched/ui/run_window.py` - Task title size, mute button, Next button
4. `tasched/ui/alert_windows.py` - Mute button on time-up

---

## TESTING CHECKLIST

- [ ] Setup window opens maximized
- [ ] Task dialog fits on screen (900x650)
- [ ] Can select different sounds for warning vs time-up
- [ ] Browse button copies sound to assets folder
- [ ] Load schedule has OK button
- [ ] Double-click loads schedule
- [ ] Mute button works on running window
- [ ] Mute button works on time-up window
- [ ] Task title wraps to multiple lines
- [ ] Ticker message saves with configuration
