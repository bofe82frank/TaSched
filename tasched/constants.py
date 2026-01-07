"""
TaSched - Task Scheduler & Countdown Orchestrator
Constants and Configuration
"""

# Application Metadata
APP_NAME = "TaSched"
APP_VERSION = "1.0.0"
APP_FULL_NAME = "TaSched - Task Scheduler & Countdown Orchestrator"
APP_TAGLINE = "Schedule your day. Run it hands-free."
COMPANY = "WAEC"
DEPARTMENT = "Technology & Innovation"
PRODUCT_NAME = "TaSched"

# Schedule Constraints
MAX_SCHEDULE_HOURS = 24

# Default Settings
DEFAULT_WARNING_POINTS = [600, 300, 60]  # 10min, 5min, 1min in seconds
DEFAULT_AUTO_ADVANCE = True
DEFAULT_GAP_BETWEEN_TASKS = 0  # seconds
DEFAULT_TIMEUP_AUTO_CLOSE = 15  # seconds
DEFAULT_WARNING_AUTO_DISMISS = 5  # seconds

# Theme Definitions
THEMES = {
    "WAEC": {
        "name": "WAEC Theme",
        "description": "Official, authoritative, academic environments",
        "background": "#002147",  # WAEC Navy Blue
        "primary_text": "#FFFFFF",
        "accent_1": "#FFB800",  # WAEC Gold
        "accent_2": "#FF4444",  # Warnings (Red)
        "accent_3": "#FFD700",  # Clock/Highlights (Gold)
        "footer": "#FFB800",
        "mood": "Formal, calm, authoritative"
    },
    "Corporate": {
        "name": "Corporate Theme",
        "description": "Enterprise productivity and office workflows",
        "background": "#1E293B",  # Dark Slate/Charcoal
        "primary_text": "#FFFFFF",
        "accent_1": "#3B82F6",  # Steel Blue
        "accent_2": "#F59E0B",  # Amber (Warnings)
        "accent_3": "#22C55E",  # Green (Success)
        "footer": "#3B82F6",
        "mood": "Clean, modern, professional"
    },
    "Indigenous": {
        "name": "Indigenous Theme",
        "description": "African-inspired, grounded authenticity",
        "background": "#0F3D2E",  # Deep Green
        "primary_text": "#FFFFFF",
        "accent_1": "#FFD700",  # Gold/Yellow
        "accent_2": "#B91C1C",  # Earth Red (Warnings)
        "accent_3": "#FAF3E0",  # Soft Cream
        "footer": "#FFD700",
        "mood": "Warm, grounded, culturally rooted"
    }
}

# Default Theme
DEFAULT_THEME = "WAEC"

# Task Modes
TASK_MODE_SEQUENTIAL = "sequential"
TASK_MODE_ABSOLUTE = "absolute"

# Task States
TASK_STATE_PENDING = "pending"
TASK_STATE_ACTIVE = "active"
TASK_STATE_PAUSED = "paused"
TASK_STATE_COMPLETED = "completed"
TASK_STATE_SKIPPED = "skipped"

# Schedule States
SCHEDULE_STATE_IDLE = "idle"
SCHEDULE_STATE_READY = "ready"
SCHEDULE_STATE_RUNNING = "running"
SCHEDULE_STATE_PAUSED = "paused"
SCHEDULE_STATE_COMPLETED = "completed"
SCHEDULE_STATE_CANCELLED = "cancelled"

# Repeat Options
REPEAT_NONE = "none"
REPEAT_DAILY = "daily"
REPEAT_CUSTOM = "custom"

# Ticker Settings
TICKER_DIRECTION_LEFT = "left"
TICKER_DIRECTION_RIGHT = "right"
TICKER_POSITION_TOP = "top"
TICKER_POSITION_BOTTOM = "bottom"
TICKER_SPEED_SLOW = 1
TICKER_SPEED_MEDIUM = 3
TICKER_SPEED_FAST = 6

# Display Modes
DISPLAY_MODE_FULLSCREEN = "fullscreen"
DISPLAY_MODE_POPUP = "popup"

# File Paths (relative to project root)
DATA_DIR = "tasched/data"
ASSETS_DIR = "tasched/assets"
IMAGES_DIR = "tasched/assets/images"
SOUNDS_DIR = "tasched/assets/sounds"

# Database
DB_FILE = "tasched.db"

# JSON Files (for templates and settings)
SETTINGS_FILE = "settings.json"
TEMPLATES_FILE = "templates.json"
LOGS_FILE = "logs.txt"

# Asset Filenames
WAEC_BACKGROUND = "WAEC_Background.png"
WAEC_LOGO = "WAEC_Logo.webp"
WAEC_ICON = "WAEC_Icon.ico"
WAEC_TONE = "WAEC_Tone.mp3"

# Window Sizes
SETUP_WINDOW_WIDTH = 900
SETUP_WINDOW_HEIGHT = 700
RUN_WINDOW_WIDTH = 800
RUN_WINDOW_HEIGHT = 600
WARNING_POPUP_WIDTH = 400
WARNING_POPUP_HEIGHT = 250
TIMEUP_WINDOW_WIDTH = 600
TIMEUP_WINDOW_HEIGHT = 400

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 16
FONT_SIZE_XLARGE = 24
FONT_SIZE_TITLE = 32
FONT_SIZE_CLOCK = 72

# Audio Settings
AUDIO_FREQUENCY = 22050
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512
