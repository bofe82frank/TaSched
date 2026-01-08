"""
TaSched - Core Data Models
Defines Task, Schedule, and Settings models
"""

import uuid
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from tasched.constants import *


@dataclass
class SoundProfile:
    """Sound configuration for a task"""
    warning_sound: str = WAEC_TONE
    timeup_sound: str = WAEC_TONE
    background_music: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SoundProfile':
        return cls(**data)


@dataclass
class DisplayOptions:
    """Display configuration for a task"""
    fullscreen_timeup: bool = True
    ticker_enabled: bool = False
    ticker_text: str = ""
    ticker_position: str = TICKER_POSITION_BOTTOM
    ticker_direction: str = TICKER_DIRECTION_LEFT
    ticker_speed: int = TICKER_SPEED_MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisplayOptions':
        return cls(**data)


@dataclass
class Task:
    """
    Represents a single task with duration, alerts, and display settings
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Task"
    duration_seconds: int = 300  # 5 minutes default
    mode: str = TASK_MODE_SEQUENTIAL
    absolute_start_time: Optional[str] = None  # HH:MM format if absolute mode
    repeat: str = REPEAT_NONE
    repeat_days: List[int] = field(default_factory=list)  # 0=Mon, 6=Sun
    warning_points_seconds: List[int] = field(default_factory=lambda: DEFAULT_WARNING_POINTS.copy())
    sound_profile: SoundProfile = field(default_factory=SoundProfile)
    display: DisplayOptions = field(default_factory=DisplayOptions)
    state: str = TASK_STATE_PENDING
    remaining_seconds: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        # Convert dict to SoundProfile if needed
        if isinstance(self.sound_profile, dict):
            self.sound_profile = SoundProfile.from_dict(self.sound_profile)
        # Convert dict to DisplayOptions if needed
        if isinstance(self.display, dict):
            self.display = DisplayOptions.from_dict(self.display)
        # Initialize remaining seconds
        if self.remaining_seconds is None:
            self.remaining_seconds = self.duration_seconds

    def reset(self):
        """Reset task to initial state"""
        self.state = TASK_STATE_PENDING
        self.remaining_seconds = self.duration_seconds
        self.started_at = None
        self.completed_at = None

    def start(self):
        """Mark task as active"""
        self.state = TASK_STATE_ACTIVE
        self.started_at = datetime.now().isoformat()

    def pause(self):
        """Pause the task"""
        self.state = TASK_STATE_PAUSED

    def resume(self):
        """Resume the task"""
        self.state = TASK_STATE_ACTIVE

    def complete(self):
        """Mark task as completed"""
        self.state = TASK_STATE_COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.remaining_seconds = 0

    def skip(self):
        """Mark task as skipped"""
        self.state = TASK_STATE_SKIPPED
        self.completed_at = datetime.now().isoformat()

    def tick(self) -> bool:
        """
        Decrement remaining time by 1 second
        Returns True if time is up (0 seconds remaining)
        """
        if self.state == TASK_STATE_ACTIVE and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            return self.remaining_seconds == 0
        return False

    def get_warning_thresholds(self) -> List[int]:
        """Get sorted warning points (descending)"""
        return sorted(self.warning_points_seconds, reverse=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        return cls(**data)


@dataclass
class Schedule:
    """
    Represents a collection of tasks to be executed in sequence
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Schedule"
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    task_ids: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    auto_start: bool = False
    auto_advance: bool = DEFAULT_AUTO_ADVANCE
    gap_between_tasks: int = DEFAULT_GAP_BETWEEN_TASKS
    state: str = SCHEDULE_STATE_IDLE
    current_task_index: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    task_prefix: str = "Now"  # Prefix for current task display (e.g., "Now", "Ongoing", etc.)

    def add_task(self, task: Task):
        """Add a task to the schedule"""
        self.tasks.append(task)
        self.task_ids.append(task.id)

    def remove_task(self, task_id: str):
        """Remove a task by ID"""
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.task_ids = [tid for tid in self.task_ids if tid != task_id]

    def reorder_tasks(self, from_index: int, to_index: int):
        """Reorder tasks in the schedule"""
        if 0 <= from_index < len(self.tasks) and 0 <= to_index < len(self.tasks):
            task = self.tasks.pop(from_index)
            self.tasks.insert(to_index, task)
            self.task_ids = [t.id for t in self.tasks]

    def duplicate_task(self, task_id: str):
        """Duplicate a task"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                new_task_dict = task.to_dict()
                new_task_dict['id'] = str(uuid.uuid4())
                new_task_dict['title'] = f"{task.title} (Copy)"
                new_task = Task.from_dict(new_task_dict)
                self.tasks.insert(i + 1, new_task)
                self.task_ids.insert(i + 1, new_task.id)
                break

    def get_current_task(self) -> Optional[Task]:
        """Get the currently active task"""
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def get_next_task(self) -> Optional[Task]:
        """Get the next task in the schedule"""
        next_index = self.current_task_index + 1
        if next_index < len(self.tasks):
            return self.tasks[next_index]
        return None

    def advance_to_next_task(self) -> bool:
        """
        Move to the next task in the schedule
        Returns True if there is a next task, False if schedule is complete
        """
        self.current_task_index += 1
        return self.current_task_index < len(self.tasks)

    def reset(self):
        """Reset schedule to initial state"""
        self.state = SCHEDULE_STATE_IDLE
        self.current_task_index = 0
        self.started_at = None
        self.completed_at = None
        for task in self.tasks:
            task.reset()

    def start(self):
        """Start the schedule"""
        self.state = SCHEDULE_STATE_RUNNING
        self.started_at = datetime.now().isoformat()
        if self.tasks:
            self.tasks[0].start()

    def pause(self):
        """Pause the schedule"""
        self.state = SCHEDULE_STATE_PAUSED
        current_task = self.get_current_task()
        if current_task:
            current_task.pause()

    def resume(self):
        """Resume the schedule"""
        self.state = SCHEDULE_STATE_RUNNING
        current_task = self.get_current_task()
        if current_task:
            current_task.resume()

    def complete(self):
        """Mark schedule as completed"""
        self.state = SCHEDULE_STATE_COMPLETED
        self.completed_at = datetime.now().isoformat()

    def cancel(self):
        """Cancel the schedule"""
        self.state = SCHEDULE_STATE_CANCELLED
        self.completed_at = datetime.now().isoformat()

    def get_total_duration(self) -> int:
        """Get total duration of all tasks in seconds"""
        return sum(task.duration_seconds for task in self.tasks)

    def validate_24_hour_constraint(self) -> bool:
        """Validate that schedule doesn't exceed 24 hours"""
        total_seconds = self.get_total_duration()
        return total_seconds <= (MAX_SCHEDULE_HOURS * 3600)

    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'task_ids': self.task_ids,
            'tasks': [task.to_dict() for task in self.tasks],
            'auto_start': self.auto_start,
            'auto_advance': self.auto_advance,
            'gap_between_tasks': self.gap_between_tasks,
            'state': self.state,
            'current_task_index': self.current_task_index,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """Create schedule from dictionary"""
        tasks_data = data.pop('tasks', [])
        schedule = cls(**data)
        schedule.tasks = [Task.from_dict(t) for t in tasks_data]
        return schedule


@dataclass
class Settings:
    """Application settings"""
    theme: str = DEFAULT_THEME
    default_warning_points: List[int] = field(default_factory=lambda: DEFAULT_WARNING_POINTS.copy())
    default_sound_warning: str = WAEC_TONE
    default_sound_timeup: str = WAEC_TONE
    default_timeup_mode: str = DISPLAY_MODE_FULLSCREEN
    default_auto_advance: bool = DEFAULT_AUTO_ADVANCE
    default_gap_between_tasks: int = DEFAULT_GAP_BETWEEN_TASKS
    default_timeup_auto_close: int = DEFAULT_TIMEUP_AUTO_CLOSE
    default_warning_auto_dismiss: int = DEFAULT_WARNING_AUTO_DISMISS
    default_ticker_enabled: bool = False
    default_ticker_position: str = TICKER_POSITION_BOTTOM
    default_ticker_direction: str = TICKER_DIRECTION_LEFT
    default_ticker_speed: int = TICKER_SPEED_MEDIUM
    window_always_on_top: bool = False
    enable_sound: bool = True
    sound_volume: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create settings from dictionary"""
        return cls(**data)
