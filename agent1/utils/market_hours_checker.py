"""
Market hours and holiday checker for Agent 1
Determines if the market is open for trading
"""
from datetime import datetime, time
from typing import List
import pytz
from config import MARKET_TIMEZONE, MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE


class MarketHoursChecker:
    """Checks if market is open, handles holidays and weekends"""

    # US Market Holidays 2025 (NYSE)
    HOLIDAYS_2025 = [
        "2025-01-01",  # New Year's Day
        "2025-01-20",  # Martin Luther King Jr. Day
        "2025-02-17",  # Presidents' Day
        "2025-04-18",  # Good Friday
        "2025-05-26",  # Memorial Day
        "2025-06-19",  # Juneteenth
        "2025-07-04",  # Independence Day
        "2025-09-01",  # Labor Day
        "2025-11-27",  # Thanksgiving
        "2025-12-25",  # Christmas
    ]

    def __init__(self):
        self.market_tz = pytz.timezone(MARKET_TIMEZONE)
        self.holidays = [datetime.strptime(d, "%Y-%m-%d").date() for d in self.HOLIDAYS_2025]

    def is_weekend(self, dt: datetime) -> bool:
        """Check if given datetime is a weekend (Saturday=5, Sunday=6)"""
        return dt.weekday() >= 5

    def is_holiday(self, dt: datetime) -> bool:
        """Check if given datetime is a market holiday"""
        return dt.date() in self.holidays

    def is_market_hours(self, dt: datetime) -> bool:
        """
        Check if given datetime is within market hours (9:30 AM - 4:00 PM ET)

        Args:
            dt: Datetime to check (will be converted to ET if needed)

        Returns:
            True if within market hours, False otherwise
        """
        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.market_tz.localize(dt)
        else:
            dt = dt.astimezone(self.market_tz)

        market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
        market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)

        return market_open <= dt.time() <= market_close

    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open

        Args:
            dt: Datetime to check (defaults to now)

        Returns:
            True if market is open, False otherwise
        """
        if dt is None:
            dt = datetime.now(self.market_tz)

        # Check weekend
        if self.is_weekend(dt):
            return False

        # Check holiday
        if self.is_holiday(dt):
            return False

        # Check market hours
        return self.is_market_hours(dt)

    def get_session(self, dt: Optional[datetime] = None) -> str:
        """
        Get current trading session

        Args:
            dt: Datetime to check (defaults to now)

        Returns:
            Session name: ASIAN, LONDON, NY_AM, NY_PM, or OTHER
        """
        from config import SESSIONS

        if dt is None:
            dt = datetime.now(self.market_tz)

        # Convert to ET if needed
        if dt.tzinfo is None:
            dt = self.market_tz.localize(dt)
        else:
            dt = dt.astimezone(self.market_tz)

        current_time = dt.time()

        for session_name, times in SESSIONS.items():
            start_str = times["start"]
            end_str = times["end"]

            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))

            start_time = time(start_hour, start_min)
            end_time = time(end_hour, end_min)

            # Handle overnight sessions (e.g., Asian session crosses midnight)
            if start_time > end_time:
                if current_time >= start_time or current_time <= end_time:
                    return session_name
            else:
                if start_time <= current_time <= end_time:
                    return session_name

        return "OTHER"


# Global instance
market_checker = MarketHoursChecker()
