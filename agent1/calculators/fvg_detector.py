"""
Fair Value Gap (FVG) detector for Agent 1
Detects 3-candle FVG patterns on 15-minute timeframe
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import INSTRUMENT, MIN_FVG_SIZE


class FVGDetector:
    """Detects Fair Value Gaps (FVG) - 3-candle imbalance patterns"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize detector

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument

    def detect_fvg(self, ohlc_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect Fair Value Gaps on 15-minute data

        Args:
            ohlc_df: DataFrame with 1-minute OHLC data

        Returns:
            List of FVG records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for FVG detection")
            return []

        try:
            # Resample to 15-minute bars
            df_15m = self._resample_to_15min(ohlc_df)

            if df_15m is None or len(df_15m) < 3:
                logger.warning("Insufficient 15-minute data for FVG detection")
                return []

            fvgs = []
            now = tz_manager.now_utc()

            # Look for FVG patterns in recent data (last 24 hours)
            lookback_start = now - timedelta(hours=24)
            recent_df = df_15m[df_15m['timestamp'] >= lookback_start]

            # Scan for 3-candle patterns
            for i in range(len(recent_df) - 2):
                candle1 = recent_df.iloc[i]
                candle2 = recent_df.iloc[i + 1]
                candle3 = recent_df.iloc[i + 2]

                # Check for bullish FVG
                bullish_fvg = self._check_bullish_fvg(candle1, candle2, candle3)
                if bullish_fvg:
                    fvgs.append(self._create_fvg_record(
                        bullish_fvg['timestamp'],
                        "BULLISH",
                        bullish_fvg['gap_top'],
                        bullish_fvg['gap_bottom'],
                        bullish_fvg['gap_size'],
                        now
                    ))

                # Check for bearish FVG
                bearish_fvg = self._check_bearish_fvg(candle1, candle2, candle3)
                if bearish_fvg:
                    fvgs.append(self._create_fvg_record(
                        bearish_fvg['timestamp'],
                        "BEARISH",
                        bearish_fvg['gap_top'],
                        bearish_fvg['gap_bottom'],
                        bearish_fvg['gap_size'],
                        now
                    ))

            logger.info(f"Detected {len(fvgs)} FVG patterns")
            return fvgs

        except Exception as e:
            logger.error(f"Error detecting FVG: {str(e)}")
            return []

    def _resample_to_15min(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Resample 1-minute data to 15-minute bars

        Args:
            df: 1-minute OHLC DataFrame

        Returns:
            15-minute OHLC DataFrame or None
        """
        try:
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
            df_copy = df_copy.set_index('timestamp')

            # Resample to 15-minute bars
            df_15m = df_copy.resample('15min').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
            }).dropna()

            df_15m = df_15m.reset_index()

            return df_15m

        except Exception as e:
            logger.error(f"Error resampling to 15-minute: {str(e)}")
            return None

    def _check_bullish_fvg(
        self,
        candle1: pd.Series,
        candle2: pd.Series,
        candle3: pd.Series
    ) -> Optional[Dict[str, Any]]:
        """
        Check for bullish FVG pattern
        Pattern: Gap between candle1 high and candle3 low (candle2 is impulse up)

        Args:
            candle1: First candle
            candle2: Middle candle (impulse)
            candle3: Third candle

        Returns:
            Dict with FVG details or None
        """
        # Bullish FVG: candle3.low > candle1.high (gap exists)
        # And candle2 should be strong bullish (impulse)

        if candle3['low'] > candle1['high']:
            gap_bottom = candle1['high']
            gap_top = candle3['low']
            gap_size = gap_top - gap_bottom

            # Check minimum gap size
            if gap_size >= MIN_FVG_SIZE:
                return {
                    'timestamp': candle2['timestamp'],  # Use middle candle time
                    'gap_top': gap_top,
                    'gap_bottom': gap_bottom,
                    'gap_size': gap_size,
                }

        return None

    def _check_bearish_fvg(
        self,
        candle1: pd.Series,
        candle2: pd.Series,
        candle3: pd.Series
    ) -> Optional[Dict[str, Any]]:
        """
        Check for bearish FVG pattern
        Pattern: Gap between candle1 low and candle3 high (candle2 is impulse down)

        Args:
            candle1: First candle
            candle2: Middle candle (impulse)
            candle3: Third candle

        Returns:
            Dict with FVG details or None
        """
        # Bearish FVG: candle3.high < candle1.low (gap exists)
        # And candle2 should be strong bearish (impulse)

        if candle3['high'] < candle1['low']:
            gap_top = candle1['low']
            gap_bottom = candle3['high']
            gap_size = gap_top - gap_bottom

            # Check minimum gap size
            if gap_size >= MIN_FVG_SIZE:
                return {
                    'timestamp': candle2['timestamp'],  # Use middle candle time
                    'gap_top': gap_top,
                    'gap_bottom': gap_bottom,
                    'gap_size': gap_size,
                }

        return None

    def _create_fvg_record(
        self,
        timestamp: datetime,
        fvg_type: str,
        gap_top: float,
        gap_bottom: float,
        gap_size: float,
        detected_at: datetime
    ) -> Dict[str, Any]:
        """
        Create an FVG record for database insertion

        Args:
            timestamp: Time of FVG formation
            fvg_type: BULLISH or BEARISH
            gap_top: Top of gap
            gap_bottom: Bottom of gap
            gap_size: Size of gap
            detected_at: Detection timestamp

        Returns:
            Dict record for database
        """
        return {
            "instrument": self.instrument,
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "fvg_type": fvg_type,
            "gap_top": round(gap_top, 2),
            "gap_bottom": round(gap_bottom, 2),
            "gap_size": round(gap_size, 2),
            "filled": False,  # Initially not filled
            "fill_timestamp": None,
        }


# Global instance
fvg_detector = FVGDetector()
