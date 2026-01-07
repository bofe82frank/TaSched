"""
TaSched - Time Service
Clock utilities and time formatting functions
"""

from datetime import datetime, time, timedelta
from typing import Tuple


class TimeService:
    """Utility class for time operations and formatting"""

    @staticmethod
    def format_seconds(seconds: int) -> str:
        """
        Format seconds as HH:MM:SS

        Args:
            seconds: Number of seconds

        Returns:
            Formatted string (e.g., "01:30:45")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_minutes_seconds(seconds: int) -> str:
        """
        Format seconds as MM:SS

        Args:
            seconds: Number of seconds

        Returns:
            Formatted string (e.g., "90:45")
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_duration(seconds: int, short: bool = False) -> str:
        """
        Format duration in human-readable format

        Args:
            seconds: Number of seconds
            short: If True, use short format (e.g., "1h 30m")

        Returns:
            Formatted string (e.g., "1 hour 30 minutes" or "1h 30m")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if short:
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if secs > 0 and hours == 0:  # Only show seconds if less than an hour
                parts.append(f"{secs}s")
            return " ".join(parts) if parts else "0s"
        else:
            parts = []
            if hours > 0:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes > 0:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if secs > 0 and hours == 0:
                parts.append(f"{secs} second{'s' if secs != 1 else ''}")
            return " ".join(parts) if parts else "0 seconds"

    @staticmethod
    def get_current_time() -> str:
        """
        Get current time as HH:MM:SS

        Returns:
            Current time string
        """
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_current_time_short() -> str:
        """
        Get current time as HH:MM

        Returns:
            Current time string
        """
        return datetime.now().strftime("%H:%M")

    @staticmethod
    def get_current_date() -> str:
        """
        Get current date as YYYY-MM-DD

        Returns:
            Current date string
        """
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_current_datetime() -> str:
        """
        Get current datetime as ISO format

        Returns:
            Current datetime string
        """
        return datetime.now().isoformat()

    @staticmethod
    def parse_time(time_str: str) -> Tuple[int, int]:
        """
        Parse time string (HH:MM or HH:MM:SS) to hours and minutes

        Args:
            time_str: Time string

        Returns:
            Tuple of (hours, minutes)
        """
        try:
            parts = time_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours, minutes
        except (ValueError, IndexError):
            return 0, 0

    @staticmethod
    def time_to_seconds(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
        """
        Convert time components to total seconds

        Args:
            hours: Number of hours
            minutes: Number of minutes
            seconds: Number of seconds

        Returns:
            Total seconds
        """
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def seconds_to_time(seconds: int) -> Tuple[int, int, int]:
        """
        Convert seconds to (hours, minutes, seconds)

        Args:
            seconds: Total seconds

        Returns:
            Tuple of (hours, minutes, seconds)
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return hours, minutes, secs

    @staticmethod
    def is_time_past(target_time: str) -> bool:
        """
        Check if target time (HH:MM) has passed today

        Args:
            target_time: Time string (HH:MM)

        Returns:
            True if time has passed, False otherwise
        """
        try:
            hours, minutes = TimeService.parse_time(target_time)
            target = time(hours, minutes)
            current = datetime.now().time()
            return current > target
        except Exception:
            return False

    @staticmethod
    def get_seconds_until(target_time: str) -> int:
        """
        Get seconds until target time (HH:MM) today

        Args:
            target_time: Time string (HH:MM)

        Returns:
            Seconds until target time (0 if time has passed)
        """
        try:
            hours, minutes = TimeService.parse_time(target_time)
            now = datetime.now()
            target = datetime.combine(now.date(), time(hours, minutes))

            if target < now:
                # Time has passed today
                return 0

            delta = target - now
            return int(delta.total_seconds())
        except Exception:
            return 0

    @staticmethod
    def add_seconds_to_time(time_str: str, seconds: int) -> str:
        """
        Add seconds to a time string and return new time

        Args:
            time_str: Time string (HH:MM:SS or HH:MM)
            seconds: Seconds to add

        Returns:
            New time string (HH:MM:SS)
        """
        try:
            # Parse the time string
            parts = time_str.split(":")
            hours = int(parts[0]) if len(parts) > 0 else 0
            minutes = int(parts[1]) if len(parts) > 1 else 0
            secs = int(parts[2]) if len(parts) > 2 else 0

            # Create a timedelta and add
            base_time = datetime.combine(datetime.today(), time(hours, minutes, secs))
            new_time = base_time + timedelta(seconds=seconds)

            return new_time.strftime("%H:%M:%S")
        except Exception:
            return "00:00:00"

    @staticmethod
    def get_friendly_time_remaining(seconds: int) -> str:
        """
        Get a friendly description of time remaining

        Args:
            seconds: Seconds remaining

        Returns:
            Friendly string (e.g., "5 minutes left", "Time's up!")
        """
        if seconds <= 0:
            return "Time's up!"
        elif seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''} left"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} left"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''} left"
            return f"{hours} hour{'s' if hours != 1 else ''} left"
