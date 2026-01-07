# TaSched - Task Scheduler & Countdown Orchestrator

**"Schedule your day. Run it hands-free."**

A professional, desktop-first task scheduling and countdown orchestration application for focused work, meetings, academic sessions, and enterprise workflows.

## Overview

TaSched allows you to plan and execute single or batched tasks across up to 24 hours with automatic sequencing, warning popups, time-up alerts, customizable sound profiles, and optional screen ticker messages while timers run in the background.

## Key Features

- **Automated Task Sequencing**: Schedule multiple tasks that run automatically one after another
- **Flexible Timing Modes**: Sequential (relative) or Absolute (clock-based) scheduling
- **Smart Warnings**: Configurable pre-alert warnings (e.g., 10min, 5min, 1min before completion)
- **Visual & Audio Alerts**: Fullscreen or popup time-up notifications with custom sounds
- **Background Operation**: Minimize the app and continue working—timers keep running
- **Theme System**: Three professional themes (WAEC, Corporate, Indigenous)
- **Template System**: Save and reuse common schedules (Pomodoro, Study Sessions, Meetings)
- **Progress Tracking**: Visual progress bars and countdown displays
- **Run History**: Complete logging and event tracking with SQLite database

## Screenshots

![TaSched Demo](docs/screenshots/demo.png) *(Coming soon)*

## Installation

### Requirements

- Python 3.13
- Windows (macOS and Linux support coming in Phase 2)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/bofe82frank/TaSched.git
cd TaSched
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## Quick Start

### Running the Demo

1. Launch TaSched
2. Click "Start Demo Schedule" to run a 3-task demo (15 seconds each)
3. Experience automatic task advancement with warnings and time-up alerts
4. Use keyboard shortcuts:
   - `Space`: Pause/Resume
   - `F11` or `ESC`: Toggle fullscreen
   - `Enter`: Dismiss alerts

### Creating Your First Schedule (Manual)

1. Create tasks with durations, warning points, and sounds
2. Add tasks to a schedule
3. Enable auto-advance for hands-free execution
4. Click "Start Schedule"
5. Setup window auto-hides, timer window takes over

## Architecture

TaSched follows a modular layered architecture:

```
tasched/
├── app.py                 # Entry point
├── ui/                    # Presentation Layer
│   ├── setup_window.py    # Schedule builder (coming soon)
│   ├── run_window.py      # Timer display
│   ├── alert_windows.py   # Warning & time-up popups
│   └── ticker_overlay.py  # Scrolling message (coming soon)
├── core/                  # Domain Layer
│   ├── models.py          # Task, Schedule, Settings
│   ├── scheduler_engine.py # State machine & execution loop
│   ├── warning_engine.py  # Threshold evaluation
│   └── time_service.py    # Clock utilities
├── services/              # Infrastructure Layer
│   ├── audio_service.py   # pygame.mixer wrapper
│   ├── storage_service.py # SQLite persistence
│   ├── log_service.py     # Text logging
│   ├── resource_service.py# Asset management
│   └── theme_service.py   # Theme engine
├── assets/
│   ├── images/            # Icons, logos, backgrounds
│   └── sounds/            # Alert tones
└── data/                  # SQLite DB, logs, settings
```

## Themes

### WAEC Theme (Default)
- **Purpose**: Official, authoritative, academic environments
- **Colors**: Navy Blue (#002147), Gold (#FFB800), White
- **Mood**: Formal, calm, authoritative

### Corporate Theme
- **Purpose**: Enterprise productivity and office workflows
- **Colors**: Dark Slate (#1E293B), Steel Blue (#3B82F6), Amber
- **Mood**: Clean, modern, professional

### Indigenous Theme
- **Purpose**: African-inspired, grounded authenticity
- **Colors**: Deep Green (#0F3D2E), Gold (#FFD700), Earth Red
- **Mood**: Warm, grounded, culturally rooted

## Configuration

### Default Settings

Settings are stored in `tasched/data/settings.json`:

```json
{
  "theme": "WAEC",
  "default_warning_points": [600, 300, 60],
  "default_timeup_mode": "fullscreen",
  "default_auto_advance": true,
  "enable_sound": true,
  "sound_volume": 0.7
}
```

### Custom Sounds

Add your own alert tones to `tasched/assets/sounds/` (MP3, WAV, OGG formats supported).

## Building Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --name="TaSched" --onefile --noconsole --icon="tasched/assets/images/WAEC_Icon.ico" --add-data="tasched/assets;tasched/assets" app.py
```

See [build_exe.md](build_exe.md) for detailed build instructions.

## Roadmap

### Phase 1 (Current) - Windows Desktop
- ✅ Core scheduler engine
- ✅ Run window with countdown timer
- ✅ Warning and time-up alerts
- ✅ Theme system (3 themes)
- ✅ SQLite persistence
- ⏳ Full setup window (schedule builder UI)
- ⏳ Ticker overlay (scrolling messages)
- ⏳ Template management UI
- ⏳ Pomodoro preset generator

### Phase 2 - Cross-Platform Desktop
- macOS support
- Linux support
- System tray icon
- Global hotkeys
- Advanced template library

### Phase 3 - Mobile Companion
- Android app
- iOS app
- Mobile-friendly timer interface

### Phase 4 - Cloud & Sync
- Cloud synchronization
- Multi-device schedule sharing
- Team collaboration features
- Analytics dashboard

## Development

### Project Structure

- **Modular Design**: Clear separation between UI, core logic, and services
- **State Machine**: Robust scheduler engine with IDLE → READY → RUNNING → PAUSED/COMPLETED states
- **PyInstaller Ready**: Asset loading compatible with both development and compiled builds
- **Extensible**: Easy to add new themes, presets, and features

### Running Tests

*(Testing framework coming soon)*

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2025 WAEC - Technology & Innovation Department

*(License to be determined)*

## Credits

- **Product Name**: TaSched (Task Scheduler + Countdown Orchestrator)
- **Company**: WAEC (West African Examinations Council)
- **Department**: Technology & Innovation
- **Version**: 1.0.0
- **Built with**: Python, Tkinter, pygame, SQLite, Pillow

## Support

For issues, questions, or feature requests:

- GitHub Issues: https://github.com/bofe82frank/TaSched/issues
- Email: bofe82frank@gmail.com

---

**TaSched** - Schedule your day. Run it hands-free.
