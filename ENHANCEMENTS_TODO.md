# TaSched Enhancement Requests

## Requested Features to Implement

### 1. Load Tone from Device ✅ (Partially Done - needs UI)
**Status**: Backend ready, needs UI button

**Implementation**:
- Add "📂 Browse..." button next to sound dropdown in TaskDialog
- Use `filedialog.askopenfilename()` to browse for .mp3/.wav files
- Copy selected file to `tasched/assets/sounds/` directory
- Refresh sound dropdown to include new file

**Code to add**:
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
        # Copy to sounds directory
        import shutil
        dest_name = os.path.basename(filename)
        dest_path = self.resource.get_sounds_path() / dest_name
        shutil.copy(filename, dest_path)

        # Refresh combo and select new file
        sound_files = self.resource.list_sound_names()
        self.sound_combo['values'] = sound_files
        self.sound_var.set(dest_name)
```

---

### 2. Warning Points in Minutes (Instead of Seconds) ✅ DONE
**Status**: UI label updated

**Current**: "Enter minutes, e.g., 10,5,1 for warnings at 10min, 5min, 1min before"

**Needs**: Update save logic to convert minutes to seconds

**Code to update** in `_save()` method:
```python
# Parse warning points (now in minutes)
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
```

---

### 3. Ticker Message Setup ⏳ (Needs Implementation)
**Status**: Needs UI fields and logic

**Requirements**:
- Text field for custom ticker message
- Support placeholders: `[TASK_NAME]`, `[NEXT_TASK]`, `[TIME_REMAINING]`
- Ticker position dropdown (Top/Bottom)
- Ticker direction dropdown (Left→Right / Right→Left)
- Ticker speed dropdown (Slow/Medium/Fast)

**UI to add** in TaskDialog:
```python
# After ticker enabled checkbox:

# Ticker Message
tk.Label(main_frame, text="Ticker Message:",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=8, column=0, sticky='w', pady=5)

self.ticker_text_entry = tk.Entry(main_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=40)
self.ticker_text_entry.grid(row=8, column=1, columnspan=2, sticky='ew', pady=5)

# Ticker Position
tk.Label(main_frame, text="Position:",
        font=(FONT_FAMILY, FONT_SIZE_SMALL),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=9, column=0, sticky='w', pady=2)

self.ticker_position_var = tk.StringVar(value="bottom")
ttk.Combobox(main_frame, textvariable=self.ticker_position_var,
             values=["top", "bottom"], state='readonly', width=15).grid(row=9, column=1, sticky='w', pady=2)

# Ticker Direction
tk.Label(main_frame, text="Direction:",
        font=(FONT_FAMILY, FONT_SIZE_SMALL),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=10, column=0, sticky='w', pady=2)

self.ticker_direction_var = tk.StringVar(value="left")
ttk.Combobox(main_frame, textvariable=self.ticker_direction_var,
             values=["left", "right"], state='readonly', width=15).grid(row=10, column=1, sticky='w', pady=2)

# Ticker Speed
tk.Label(main_frame, text="Speed:",
        font=(FONT_FAMILY, FONT_SIZE_SMALL),
        bg=self.theme.background, fg=self.theme.primary_text).grid(row=11, column=0, sticky='w', pady=2)

self.ticker_speed_var = tk.StringVar(value="medium")
ttk.Combobox(main_frame, textvariable=self.ticker_speed_var,
             values=["slow", "medium", "fast"], state='readonly', width=15).grid(row=11, column=1, sticky='w', pady=2)
```

**Save logic** to update:
```python
# Ticker settings
self.task.display.ticker_enabled = self.ticker_enabled_var.get()
self.task.display.ticker_text = self.ticker_text_entry.get()
self.task.display.ticker_position = self.ticker_position_var.get()
self.task.display.ticker_direction = self.ticker_direction_var.get()

# Map speed to pixel value
speed_map = {"slow": 1, "medium": 3, "fast": 6}
self.task.display.ticker_speed = speed_map.get(self.ticker_speed_var.get(), 3)
```

---

## Additional Enhancements for Next Steps

### 4. Ticker Overlay Window Implementation
**File**: `tasched/ui/ticker_overlay.py`

Create borderless window that scrolls text across screen top/bottom.

### 5. Template Management UI
- Quick-load Pomodoro (25/5 cycles)
- Save current schedule as template
- Template library view

### 6. Settings Window
- Theme selector
- Default warning points
- Default sounds
- Volume control
- Auto-advance settings

### 7. Run History Viewer
- View past schedule runs
- Export to CSV/JSON
- Statistics and charts

---

## Priority Order

**HIGH PRIORITY** (Immediate):
1. Warning points in minutes (backend conversion) ✅
2. Ticker message UI fields
3. Browse for sound file

**MEDIUM PRIORITY** (This Week):
4. Ticker overlay implementation
5. Template quick-load UI

**LOW PRIORITY** (Future):
6. Settings window
7. Run history viewer
8. Analytics dashboard

---

## Files to Modify

1. `tasched/ui/setup_window.py` - Add browse button, ticker fields, warning conversion
2. `tasched/ui/ticker_overlay.py` - NEW FILE - Implement scrolling overlay
3. `tasched/core/models.py` - Ensure DisplayOptions has all ticker fields
4. `app.py` - Integrate ticker overlay when task runs

---

## Testing Checklist

- [ ] Browse and add custom sound file
- [ ] Warning points entered as minutes convert to seconds correctly
- [ ] Ticker message saves with task
- [ ] Ticker displays during task execution
- [ ] Ticker position/direction/speed work as configured
- [ ] Placeholders replaced in ticker message ([TASK_NAME], etc.)
