"""
TaSched - Storage Service
SQLite database management for schedules, tasks, and run history
JSON for settings and templates
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from tasched.core.models import Task, Schedule, Settings
from tasched.services.resource_service import get_resource_service


class StorageService:
    """
    Manages persistence using SQLite for data and JSON for settings/templates
    """

    def __init__(self, db_path: str = None):
        resource_service = get_resource_service()

        # Set database path
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = resource_service.get_data_file("tasched.db")

        # Set JSON file paths
        self.settings_path = resource_service.get_data_file("settings.json")
        self.templates_path = resource_service.get_data_file("templates.json")

        # Initialize database
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                mode TEXT NOT NULL,
                absolute_start_time TEXT,
                repeat TEXT,
                repeat_days TEXT,
                warning_points_seconds TEXT,
                sound_profile TEXT,
                display_options TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # Schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                task_ids TEXT,
                auto_start INTEGER,
                auto_advance INTEGER,
                gap_between_tasks INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # Run history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id TEXT,
                schedule_name TEXT,
                event_type TEXT,
                event_data TEXT,
                timestamp TEXT
            )
        ''')

        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                schedule_data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    # ========== Task Operations ==========

    def save_task(self, task: Task):
        """Save or update a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        task_dict = task.to_dict()
        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO tasks (
                id, title, duration_seconds, mode, absolute_start_time,
                repeat, repeat_days, warning_points_seconds, sound_profile,
                display_options, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM tasks WHERE id = ?), ?), ?)
        ''', (
            task.id,
            task.title,
            task.duration_seconds,
            task.mode,
            task.absolute_start_time,
            task.repeat,
            json.dumps(task.repeat_days),
            json.dumps(task.warning_points_seconds),
            json.dumps(task.sound_profile.to_dict()),
            json.dumps(task.display.to_dict()),
            task.id,  # For COALESCE
            now,      # If new
            now       # updated_at
        ))

        conn.commit()
        conn.close()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_task(row)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def delete_task(self, task_id: str):
        """Delete a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object"""
        return Task(
            id=row[0],
            title=row[1],
            duration_seconds=row[2],
            mode=row[3],
            absolute_start_time=row[4],
            repeat=row[5],
            repeat_days=json.loads(row[6]) if row[6] else [],
            warning_points_seconds=json.loads(row[7]) if row[7] else [],
            sound_profile=json.loads(row[8]) if row[8] else {},
            display=json.loads(row[9]) if row[9] else {}
        )

    # ========== Schedule Operations ==========

    def save_schedule(self, schedule: Schedule):
        """Save or update a schedule (and its tasks)"""
        # Save all tasks first
        for task in schedule.tasks:
            self.save_task(task)

        # Save schedule
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO schedules (
                id, name, date, task_ids, auto_start, auto_advance,
                gap_between_tasks, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM schedules WHERE id = ?), ?), ?)
        ''', (
            schedule.id,
            schedule.name,
            schedule.date,
            json.dumps(schedule.task_ids),
            1 if schedule.auto_start else 0,
            1 if schedule.auto_advance else 0,
            schedule.gap_between_tasks,
            schedule.id,  # For COALESCE
            now,          # If new
            now           # updated_at
        ))

        conn.commit()
        conn.close()

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a schedule by ID (with tasks)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_schedule(row)

    def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM schedules ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_schedule(row) for row in rows]

    def delete_schedule(self, schedule_id: str):
        """Delete a schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        conn.commit()
        conn.close()

    def _row_to_schedule(self, row) -> Schedule:
        """Convert database row to Schedule object"""
        task_ids = json.loads(row[3]) if row[3] else []
        tasks = [self.get_task(tid) for tid in task_ids]
        tasks = [t for t in tasks if t is not None]  # Filter out None values

        return Schedule(
            id=row[0],
            name=row[1],
            date=row[2],
            task_ids=task_ids,
            tasks=tasks,
            auto_start=bool(row[4]),
            auto_advance=bool(row[5]),
            gap_between_tasks=row[6],
            created_at=row[7]
        )

    # ========== Template Operations ==========

    def save_template(self, name: str, description: str, schedule: Schedule):
        """Save a schedule as a template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        template_id = f"template_{name.lower().replace(' ', '_')}"
        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO templates (
                id, name, description, schedule_data, created_at, updated_at
            ) VALUES (?, ?, ?, ?,
                COALESCE((SELECT created_at FROM templates WHERE id = ?), ?), ?)
        ''', (
            template_id,
            name,
            description,
            json.dumps(schedule.to_dict()),
            template_id,  # For COALESCE
            now,          # If new
            now           # updated_at
        ))

        conn.commit()
        conn.close()

    def get_template(self, template_id: str) -> Optional[Schedule]:
        """Get a template by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT schedule_data FROM templates WHERE id = ?', (template_id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            return None

        schedule_data = json.loads(row[0])
        return Schedule.from_dict(schedule_data)

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, description FROM templates ORDER BY name')
        rows = cursor.fetchall()
        conn.close()

        return [
            {'id': row[0], 'name': row[1], 'description': row[2]}
            for row in rows
        ]

    def delete_template(self, template_id: str):
        """Delete a template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()

    # ========== Run History ==========

    def log_event(self, schedule_id: str, schedule_name: str, event_type: str, event_data: Dict[str, Any] = None):
        """Log a schedule run event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO run_history (schedule_id, schedule_name, event_type, event_data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            schedule_id,
            schedule_name,
            event_type,
            json.dumps(event_data) if event_data else None,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_run_history(self, schedule_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get run history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if schedule_id:
            cursor.execute('''
                SELECT * FROM run_history WHERE schedule_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (schedule_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM run_history ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'id': row[0],
                'schedule_id': row[1],
                'schedule_name': row[2],
                'event_type': row[3],
                'event_data': json.loads(row[4]) if row[4] else None,
                'timestamp': row[5]
            }
            for row in rows
        ]

    # ========== Settings (JSON) ==========

    def save_settings(self, settings: Settings):
        """Save settings to JSON file"""
        with open(self.settings_path, 'w') as f:
            json.dump(settings.to_dict(), f, indent=2)

    def load_settings(self) -> Settings:
        """Load settings from JSON file"""
        if not Path(self.settings_path).exists():
            # Return default settings
            return Settings()

        try:
            with open(self.settings_path, 'r') as f:
                data = json.load(f)
            return Settings.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return Settings()


# Global storage service instance
_storage_service = None


def get_storage_service() -> StorageService:
    """
    Get or create the global storage service instance

    Returns:
        StorageService instance
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
