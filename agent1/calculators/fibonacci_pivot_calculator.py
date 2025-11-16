"""
Fibonacci pivot calculator for Agent 1
Calculates weekly and daily Fibonacci pivot points (S3, S2, S1, PP, R1, R2, R3)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import INSTRUMENT


class FibonacciPivotCalculator:
    """Calculates Fibonacci pivot points"""

    # Fibonacci ratios
    RATIOS = {
        'R3': 1.000,
        'R2': 0.618,
        'R1': 0.382,
        'S1': 0.382,
        'S2': 0.618,
        'S3': 1.000,
    }

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize calculator

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument

    def calculate_pivots(self, ohlc_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calculate both weekly and daily Fibonacci pivots

        Args:
            ohlc_df: DataFrame with OHLC data

        Returns:
            List of pivot records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for pivot calculation")
            return []

        pivots = []
        now = tz_manager.now_utc()

        try:
            # Calculate weekly pivots
            weekly_pivots = self._calculate_period_pivots(ohlc_df, "WEEKLY", now)
            if weekly_pivots:
                pivots.extend(weekly_pivots)

            # Calculate daily pivots
            daily_pivots = self._calculate_period_pivots(ohlc_df, "DAILY", now)
            if daily_pivots:
                pivots.extend(daily_pivots)

            logger.info(f"Calculated {len(pivots)} pivot points")
            return pivots

        except Exception as e:
            logger.error(f"Error calculating pivots: {str(e)}")
            return []

    def _calculate_period_pivots(
        self,
        df: pd.DataFrame,
        period: str,
        now: datetime
    ) -> List[Dict[str, Any]]:
        """
        Calculate pivots for a specific period (WEEKLY or DAILY)

        Args:
            df: OHLC DataFrame
            period: 'WEEKLY' or 'DAILY'
            now: Current datetime

        Returns:
            List of pivot records
        """
        # Get the previous period's H, L, C
        if period == "WEEKLY":
            prev_hl = self._get_previous_week_hlc(df, now)
        elif period == "DAILY":
            prev_hl = self._get_previous_day_hlc(df, now)
        else:
            logger.error(f"Unknown period: {period}")
            return []

        if prev_hl is None:
            logger.warning(f"No data for {period} pivot calculation")
            return []

        high = prev_hl['high']
        low = prev_hl['low']
        close = prev_hl['close']

        # Calculate Pivot Point (PP)
        pp = (high + low + close) / 3

        # Calculate range
        range_val = high - low

        # Calculate support and resistance levels using Fibonacci ratios
        pivots = []

        # Pivot Point
        pivots.append(self._create_pivot_record(f"{period}_PP", pp, now))

        # Resistance levels
        pivots.append(self._create_pivot_record(
            f"{period}_R1",
            pp + (self.RATIOS['R1'] * range_val),
            now
        ))
        pivots.append(self._create_pivot_record(
            f"{period}_R2",
            pp + (self.RATIOS['R2'] * range_val),
            now
        ))
        pivots.append(self._create_pivot_record(
            f"{period}_R3",
            pp + (self.RATIOS['R3'] * range_val),
            now
        ))

        # Support levels
        pivots.append(self._create_pivot_record(
            f"{period}_S1",
            pp - (self.RATIOS['S1'] * range_val),
            now
        ))
        pivots.append(self._create_pivot_record(
            f"{period}_S2",
            pp - (self.RATIOS['S2'] * range_val),
            now
        ))
        pivots.append(self._create_pivot_record(
            f"{period}_S3",
            pp - (self.RATIOS['S3'] * range_val),
            now
        ))

        logger.debug(f"Calculated {period} pivots: PP={pp:.2f}, H={high:.2f}, L={low:.2f}, C={close:.2f}")
        return pivots

    def _get_previous_week_hlc(self, df: pd.DataFrame, now: datetime) -> Optional[Dict[str, float]]:
        """Get previous week's high, low, close"""
        try:
            # Previous week (Monday to Sunday)
            current_week_start = tz_manager.get_week_start_utc(now)
            prev_week_start = current_week_start - timedelta(days=7)
            prev_week_end = current_week_start - timedelta(seconds=1)

            # Filter data
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

            mask = (df_copy['timestamp'] >= prev_week_start) & (df_copy['timestamp'] <= prev_week_end)
            week_df = df_copy[mask]

            if week_df.empty:
                return None

            return {
                'high': float(week_df['high'].max()),
                'low': float(week_df['low'].min()),
                'close': float(week_df.iloc[-1]['close']),
            }

        except Exception as e:
            logger.error(f"Error getting previous week HLC: {str(e)}")
            return None

    def _get_previous_day_hlc(self, df: pd.DataFrame, now: datetime) -> Optional[Dict[str, float]]:
        """Get previous day's high, low, close"""
        try:
            # Previous day (00:00 to 23:59 UTC)
            prev_day_start = tz_manager.get_day_start_utc(now) - timedelta(days=1)
            prev_day_end = prev_day_start + timedelta(hours=23, minutes=59, seconds=59)

            # Filter data
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

            mask = (df_copy['timestamp'] >= prev_day_start) & (df_copy['timestamp'] <= prev_day_end)
            day_df = df_copy[mask]

            if day_df.empty:
                return None

            return {
                'high': float(day_df['high'].max()),
                'low': float(day_df['low'].min()),
                'close': float(day_df.iloc[-1]['close']),
            }

        except Exception as e:
            logger.error(f"Error getting previous day HLC: {str(e)}")
            return None

    def _create_pivot_record(self, pivot_type: str, price: float, timestamp: datetime) -> Dict[str, Any]:
        """
        Create a pivot record for database insertion

        Args:
            pivot_type: Type of pivot (e.g., WEEKLY_R1, DAILY_S2)
            price: Price level
            timestamp: Timestamp for the record

        Returns:
            Dict record for database
        """
        # Determine period and level
        parts = pivot_type.split('_')
        period = parts[0]  # WEEKLY or DAILY
        level = parts[1]   # PP, R1, R2, R3, S1, S2, S3

        return {
            "instrument": self.instrument,
            "timestamp": timestamp.isoformat(),
            "period": period,
            "level": level,
            "price": round(price, 2),
        }


# Global instance
fib_calculator = FibonacciPivotCalculator()
