"""
Timezone management utilities for Agent 1
Handles conversion between ET (Eastern Time) and UTC
"""
from datetime import datetime, time
from typing import Optional
import pytz
from config import MARKET_TIMEZONE, UTC_TIMEZONE


class TimezoneManager:
    """Manages timezone conversions between ET and UTC"""

    def __init__(self):
        self.et_tz = pytz.timezone(MARKET_TIMEZONE)
        self.utc_tz = pytz.timezone(UTC_TIMEZONE)

    def now_et(self) -> datetime:
        """Get current time in ET"""
        return datetime.now(self.et_tz)

    def now_utc(self) -> datetime:
        """Get current time in UTC"""
        return datetime.now(self.utc_tz)

    def et_to_utc(self, dt: datetime) -> datetime:
        """
        Convert ET datetime to UTC

        Args:
            dt: Datetime in ET timezone

        Returns:
            Datetime in UTC timezone
        """
        if dt.tzinfo is None:
            dt = self.et_tz.localize(dt)
        return dt.astimezone(self.utc_tz)

    def utc_to_et(self, dt: datetime) -> datetime:
        """
        Convert UTC datetime to ET

        Args:
            dt: Datetime in UTC timezone

        Returns:
            Datetime in ET timezone
        """
        if dt.tzinfo is None:
            dt = self.utc_tz.localize(dt)
        return dt.astimezone(self.et_tz)

    def get_ny_open_utc(self, date: Optional[datetime] = None) -> datetime:
        """
        Get NY session open (13:30 UTC / 08:30 ET) for a given date

        Args:
            date: Date to get NY open for (defaults to today)

        Returns:
            NY open datetime in UTC
        """
        if date is None:
            date = self.now_et()

        # Create NY open time (8:30 AM ET)
        ny_open_et = self.et_tz.localize(
            datetime.combine(date.date(), time(8, 30))
        )
        return self.et_to_utc(ny_open_et)

    def get_session_start_utc(self, session_name: str, date: Optional[datetime] = None) -> datetime:
        """
        Get session start time in UTC

        Args:
            session_name: Session name (ASIAN, LONDON, NY_AM, NY_PM)
            date: Date to get session start for (defaults to today)

        Returns:
            Session start datetime in UTC
        """
        from config import SESSIONS

        if date is None:
            date = self.now_et()

        if session_name not in SESSIONS:
            raise ValueError(f"Unknown session: {session_name}")

        start_time_str = SESSIONS[session_name]["start"]
        hour, minute = map(int, start_time_str.split(":"))

        # Create session start time in ET
        session_start_et = self.et_tz.localize(
            datetime.combine(date.date(), time(hour, minute))
        )
        return self.et_to_utc(session_start_et)

    def get_day_start_utc(self, date: Optional[datetime] = None) -> datetime:
        """
        Get day start (00:00 UTC) for a given date

        Args:
            date: Date to get start for (defaults to today)

        Returns:
            Day start datetime in UTC
        """
        if date is None:
            date = self.now_utc()

        return self.utc_tz.localize(
            datetime.combine(date.date(), time(0, 0))
        )

    def get_week_start_utc(self, date: Optional[datetime] = None) -> datetime:
        """
        Get week start (Monday 00:00 UTC) for a given date

        Args:
            date: Date to get week start for (defaults to today)

        Returns:
            Week start datetime in UTC
        """
        if date is None:
            date = self.now_utc()

        # Find Monday of this week
        days_since_monday = date.weekday()
        monday = date.date() - pytz.timedelta(days=days_since_monday)

        return self.utc_tz.localize(
            datetime.combine(monday, time(0, 0))
        )

    def get_month_start_utc(self, date: Optional[datetime] = None) -> datetime:
        """
        Get month start (1st day, 00:00 UTC) for a given date

        Args:
            date: Date to get month start for (defaults to today)

        Returns:
            Month start datetime in UTC
        """
        if date is None:
            date = self.now_utc()

        return self.utc_tz.localize(
            datetime.combine(date.replace(day=1).date(), time(0, 0))
        )


# Global instance
tz_manager = TimezoneManager()
