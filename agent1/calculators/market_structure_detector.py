"""
Market structure detector for Agent 1
Detects Break of Structure (BOS) and Change of Character (CHoCH) events
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import (
    INSTRUMENT,
    STRUCTURE_BREAK_TYPES,
    STRONG_DISPLACEMENT_PIPS,
    STRONG_DISPLACEMENT_MINUTES
)


class MarketStructureDetector:
    """Detects market structure breaks (BOS/CHoCH) on multiple timeframes"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize detector

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument

    def detect_structure(
        self,
        ohlc_df: pd.DataFrame,
        timeframes: List[str] = ["15min", "1H", "4H"]
    ) -> List[Dict[str, Any]]:
        """
        Detect market structure breaks on multiple timeframes

        Args:
            ohlc_df: DataFrame with 1-minute OHLC data
            timeframes: List of timeframes to analyze

        Returns:
            List of structure break records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for structure detection")
            return []

        structure_breaks = []

        try:
            for timeframe in timeframes:
                # Resample to timeframe
                tf_df = self._resample_to_timeframe(ohlc_df, timeframe)

                if tf_df is None or len(tf_df) < 3:
                    continue

                # Detect breaks on this timeframe
                breaks = self._detect_breaks_on_timeframe(tf_df, timeframe)
                structure_breaks.extend(breaks)

            logger.info(f"Detected {len(structure_breaks)} structure breaks")
            return structure_breaks

        except Exception as e:
            logger.error(f"Error detecting market structure: {str(e)}")
            return []

    def _resample_to_timeframe(self, df: pd.DataFrame, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Resample data to specified timeframe

        Args:
            df: 1-minute OHLC DataFrame
            timeframe: Timeframe string (e.g., '15min', '1H', '4H')

        Returns:
            Resampled DataFrame or None
        """
        try:
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
            df_copy = df_copy.set_index('timestamp')

            # Resample
            df_resampled = df_copy.resample(timeframe).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
            }).dropna()

            df_resampled = df_resampled.reset_index()

            return df_resampled

        except Exception as e:
            logger.error(f"Error resampling to {timeframe}: {str(e)}")
            return None

    def _detect_breaks_on_timeframe(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> List[Dict[str, Any]]:
        """
        Detect structure breaks on a specific timeframe

        Args:
            df: Timeframe OHLC data
            timeframe: Timeframe string

        Returns:
            List of break records
        """
        breaks = []
        now = tz_manager.now_utc()

        # Look back 7 days
        lookback_start = now - timedelta(days=7)
        recent_df = df[df['timestamp'] >= lookback_start]

        if len(recent_df) < 3:
            return []

        # Track swing highs and lows
        swing_highs, swing_lows = self._identify_swings(recent_df)

        # Detect BOS (Break of Structure)
        # - Bullish BOS: Price breaks above previous swing high
        # - Bearish BOS: Price breaks below previous swing low

        for i in range(1, len(recent_df)):
            current_bar = recent_df.iloc[i]
            prev_bar = recent_df.iloc[i - 1]

            # Check for bullish BOS (break above swing high)
            if swing_highs:
                last_swing_high = swing_highs[-1]['price']
                if current_bar['high'] > last_swing_high and prev_bar['high'] <= last_swing_high:
                    # Calculate displacement
                    displacement = self._calculate_displacement(current_bar, prev_bar)

                    breaks.append(self._create_structure_record(
                        current_bar['timestamp'],
                        "BOS",
                        "BULLISH",
                        timeframe,
                        last_swing_high,
                        displacement,
                        now
                    ))

            # Check for bearish BOS (break below swing low)
            if swing_lows:
                last_swing_low = swing_lows[-1]['price']
                if current_bar['low'] < last_swing_low and prev_bar['low'] >= last_swing_low:
                    # Calculate displacement
                    displacement = self._calculate_displacement(current_bar, prev_bar)

                    breaks.append(self._create_structure_record(
                        current_bar['timestamp'],
                        "BOS",
                        "BEARISH",
                        timeframe,
                        last_swing_low,
                        displacement,
                        now
                    ))

        # Detect CHoCH (Change of Character)
        # CHoCH occurs when market breaks counter-trend structure
        # Simplified: detect when trend reverses (higher highs to lower highs, or vice versa)

        choch_breaks = self._detect_choch(recent_df, timeframe, now)
        breaks.extend(choch_breaks)

        return breaks

    def _identify_swings(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Identify swing highs and lows

        Args:
            df: OHLC DataFrame

        Returns:
            Tuple of (swing_highs, swing_lows)
        """
        swing_highs = []
        swing_lows = []

        # Simple swing detection: local maxima/minima with 2-bar lookback/forward
        for i in range(2, len(df) - 2):
            bar = df.iloc[i]

            # Swing high: high is higher than 2 bars before and 2 bars after
            if (bar['high'] > df.iloc[i-1]['high'] and
                bar['high'] > df.iloc[i-2]['high'] and
                bar['high'] > df.iloc[i+1]['high'] and
                bar['high'] > df.iloc[i+2]['high']):

                swing_highs.append({
                    'timestamp': bar['timestamp'],
                    'price': bar['high']
                })

            # Swing low: low is lower than 2 bars before and 2 bars after
            if (bar['low'] < df.iloc[i-1]['low'] and
                bar['low'] < df.iloc[i-2]['low'] and
                bar['low'] < df.iloc[i+1]['low'] and
                bar['low'] < df.iloc[i+2]['low']):

                swing_lows.append({
                    'timestamp': bar['timestamp'],
                    'price': bar['low']
                })

        return swing_highs, swing_lows

    def _detect_choch(self, df: pd.DataFrame, timeframe: str, now: datetime) -> List[Dict[str, Any]]:
        """
        Detect Change of Character (CHoCH) events

        Args:
            df: OHLC DataFrame
            timeframe: Timeframe string
            now: Current time

        Returns:
            List of CHoCH records
        """
        # Simplified CHoCH detection
        # CHoCH: When price fails to make a new high/low and reverses

        choch_events = []

        swing_highs, swing_lows = self._identify_swings(df)

        # Check for bullish CHoCH (failure to make lower low, then breaks structure upward)
        if len(swing_lows) >= 2:
            # If latest swing low is higher than previous (failure to make lower low)
            if swing_lows[-1]['price'] > swing_lows[-2]['price']:
                choch_events.append(self._create_structure_record(
                    swing_lows[-1]['timestamp'],
                    "CHOCH",
                    "BULLISH",
                    timeframe,
                    swing_lows[-1]['price'],
                    {"speed": 0, "quality": "MEDIUM"},
                    now
                ))

        # Check for bearish CHoCH (failure to make higher high, then breaks structure downward)
        if len(swing_highs) >= 2:
            # If latest swing high is lower than previous (failure to make higher high)
            if swing_highs[-1]['price'] < swing_highs[-2]['price']:
                choch_events.append(self._create_structure_record(
                    swing_highs[-1]['timestamp'],
                    "CHOCH",
                    "BEARISH",
                    timeframe,
                    swing_highs[-1]['price'],
                    {"speed": 0, "quality": "MEDIUM"},
                    now
                ))

        return choch_events

    def _calculate_displacement(self, current_bar: pd.Series, prev_bar: pd.Series) -> Dict[str, Any]:
        """
        Calculate displacement speed and quality

        Args:
            current_bar: Current bar
            prev_bar: Previous bar

        Returns:
            Dict with displacement metrics
        """
        # Calculate pips moved
        move = abs(current_bar['close'] - prev_bar['close'])

        # Assume 1-minute bars for speed calculation (adjust based on timeframe)
        # Strong displacement: > 20 pips in < 15 minutes

        quality = "STRONG" if move >= STRONG_DISPLACEMENT_PIPS else "WEAK"

        return {
            "speed": round(move, 2),
            "quality": quality
        }

    def _create_structure_record(
        self,
        timestamp: datetime,
        break_type: str,
        direction: str,
        timeframe: str,
        level: float,
        displacement: Dict[str, Any],
        detected_at: datetime
    ) -> Dict[str, Any]:
        """
        Create a structure break record for database insertion

        Args:
            timestamp: Time of break
            break_type: BOS or CHOCH
            direction: BULLISH or BEARISH
            timeframe: Timeframe
            level: Price level broken
            displacement: Displacement metrics
            detected_at: Detection timestamp

        Returns:
            Dict record for database
        """
        # Determine break weight
        if displacement['quality'] == "STRONG":
            break_weight = STRUCTURE_BREAK_TYPES['MAJOR']
        elif displacement['quality'] == "MEDIUM":
            break_weight = STRUCTURE_BREAK_TYPES['INTERMEDIATE']
        else:
            break_weight = STRUCTURE_BREAK_TYPES['MINOR']

        return {
            "instrument": self.instrument,
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "break_type": break_type,
            "direction": direction,
            "timeframe": timeframe,
            "level": round(level, 2),
            "displacement_speed": displacement.get('speed', 0),
            "break_weight": round(break_weight, 2),
        }


# Global instance
structure_detector = MarketStructureDetector()
