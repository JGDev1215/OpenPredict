"""
Reference level calculator for Agent 1
Calculates 8 key ICT reference levels (opens and session highs/lows)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import INSTRUMENT


class ReferenceLevelCalculator:
    """Calculates ICT reference levels (opens and key highs/lows)"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize calculator

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument

    def calculate_all_levels(self, ohlc_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calculate all 8 reference levels

        Args:
            ohlc_df: DataFrame with OHLC data

        Returns:
            List of reference level records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for reference level calculation")
            return []

        now = tz_manager.now_utc()
        levels = []

        try:
            # 1. Weekly Open (Monday 00:00 UTC)
            week_start = tz_manager.get_week_start_utc(now)
            weekly_open = self._get_open_price_at(ohlc_df, week_start)
            if weekly_open is not None:
                levels.append(self._create_level_record("WEEKLY_OPEN", weekly_open, now))

            # 2. Monthly Open (1st day 00:00 UTC)
            month_start = tz_manager.get_month_start_utc(now)
            monthly_open = self._get_open_price_at(ohlc_df, month_start)
            if monthly_open is not None:
                levels.append(self._create_level_record("MONTHLY_OPEN", monthly_open, now))

            # 3. Daily Open (00:00 UTC)
            day_start = tz_manager.get_day_start_utc(now)
            daily_open = self._get_open_price_at(ohlc_df, day_start)
            if daily_open is not None:
                levels.append(self._create_level_record("DAILY_OPEN", daily_open, now))

            # 4. NY Open (13:30 UTC / 08:30 ET)
            ny_open_time = tz_manager.get_ny_open_utc(now)
            ny_open = self._get_open_price_at(ohlc_df, ny_open_time)
            if ny_open is not None:
                levels.append(self._create_level_record("NY_OPEN", ny_open, now))

            # 5. 4H Open
            four_hour_open = self._get_4h_open(ohlc_df, now)
            if four_hour_open is not None:
                levels.append(self._create_level_record("4H_OPEN", four_hour_open, now))

            # 6. 1H Open
            one_hour_open = self._get_1h_open(ohlc_df, now)
            if one_hour_open is not None:
                levels.append(self._create_level_record("1H_OPEN", one_hour_open, now))

            # 7. Asian Session High/Low
            asian_hl = self._get_asian_session_high_low(ohlc_df, now)
            if asian_hl:
                levels.append(self._create_level_record("ASIAN_HIGH", asian_hl['high'], now))
                levels.append(self._create_level_record("ASIAN_LOW", asian_hl['low'], now))

            # 8. Previous Day High/Low
            prev_day_hl = self._get_previous_day_high_low(ohlc_df, now)
            if prev_day_hl:
                levels.append(self._create_level_record("PREV_DAY_HIGH", prev_day_hl['high'], now))
                levels.append(self._create_level_record("PREV_DAY_LOW", prev_day_hl['low'], now))

            logger.info(f"Calculated {len(levels)} reference levels")
            return levels

        except Exception as e:
            logger.error(f"Error calculating reference levels: {str(e)}")
            return []

    def _get_open_price_at(self, df: pd.DataFrame, target_time: datetime) -> Optional[float]:
        """
        Get open price at or near a specific time

        Args:
            df: OHLC DataFrame
            target_time: Target datetime

        Returns:
            Open price or None
        """
        # Find the closest bar at or after the target time
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

        # Get bars at or after target time
        mask = df_copy['timestamp'] >= target_time
        filtered = df_copy[mask]

        if filtered.empty:
            logger.debug(f"No data found at or after {target_time}")
            return None

        # Return the open of the first bar
        return float(filtered.iloc[0]['open'])

    def _get_4h_open(self, df: pd.DataFrame, now: datetime) -> Optional[float]:
        """Get current 4-hour period open"""
        # Find the start of current 4-hour period
        hour = now.hour
        period_start_hour = (hour // 4) * 4
        period_start = now.replace(hour=period_start_hour, minute=0, second=0, microsecond=0)

        return self._get_open_price_at(df, period_start)

    def _get_1h_open(self, df: pd.DataFrame, now: datetime) -> Optional[float]:
        """Get current 1-hour period open"""
        # Find the start of current hour
        hour_start = now.replace(minute=0, second=0, microsecond=0)

        return self._get_open_price_at(df, hour_start)

    def _get_asian_session_high_low(self, df: pd.DataFrame, now: datetime) -> Optional[Dict[str, float]]:
        """
        Get Asian session high/low (18:00 ET to 02:00 ET)

        Args:
            df: OHLC DataFrame
            now: Current datetime

        Returns:
            Dict with 'high' and 'low' or None
        """
        try:
            # Asian session is 18:00 ET previous day to 02:00 ET current day
            # Convert to UTC
            now_et = tz_manager.utc_to_et(now)

            # If current time is before 02:00 ET, use yesterday's asian session
            if now_et.hour < 2:
                session_date = now_et.date() - timedelta(days=1)
            else:
                session_date = now_et.date()

            # Session start: 18:00 ET (previous day in some cases)
            session_start_et = tz_manager.et_tz.localize(
                datetime.combine(session_date, datetime.strptime("18:00", "%H:%M").time())
            )
            # Session end: 02:00 ET (next day)
            session_end_et = session_start_et + timedelta(hours=8)

            session_start_utc = tz_manager.et_to_utc(session_start_et)
            session_end_utc = tz_manager.et_to_utc(session_end_et)

            # Filter data
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

            mask = (df_copy['timestamp'] >= session_start_utc) & (df_copy['timestamp'] <= session_end_utc)
            session_df = df_copy[mask]

            if session_df.empty:
                return None

            return {
                'high': float(session_df['high'].max()),
                'low': float(session_df['low'].min()),
            }

        except Exception as e:
            logger.error(f"Error calculating Asian session high/low: {str(e)}")
            return None

    def _get_previous_day_high_low(self, df: pd.DataFrame, now: datetime) -> Optional[Dict[str, float]]:
        """
        Get previous day high/low

        Args:
            df: OHLC DataFrame
            now: Current datetime

        Returns:
            Dict with 'high' and 'low' or None
        """
        try:
            # Previous day (00:00 to 23:59 UTC)
            prev_day_start = tz_manager.get_day_start_utc(now) - timedelta(days=1)
            prev_day_end = prev_day_start + timedelta(hours=23, minutes=59, seconds=59)

            # Filter data
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

            mask = (df_copy['timestamp'] >= prev_day_start) & (df_copy['timestamp'] <= prev_day_end)
            prev_day_df = df_copy[mask]

            if prev_day_df.empty:
                return None

            return {
                'high': float(prev_day_df['high'].max()),
                'low': float(prev_day_df['low'].min()),
            }

        except Exception as e:
            logger.error(f"Error calculating previous day high/low: {str(e)}")
            return None

    def _create_level_record(self, level_type: str, price: float, timestamp: datetime) -> Dict[str, Any]:
        """
        Create a reference level record for database insertion

        Args:
            level_type: Type of level (e.g., WEEKLY_OPEN, NY_OPEN)
            price: Price level
            timestamp: Timestamp for the record

        Returns:
            Dict record for database
        """
        return {
            "instrument": self.instrument,
            "timestamp": timestamp.isoformat(),
            "level_type": level_type,
            "price": round(price, 2),
        }


# Global instance
ref_calculator = ReferenceLevelCalculator()
