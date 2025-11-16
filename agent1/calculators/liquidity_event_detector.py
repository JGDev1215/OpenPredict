"""
Liquidity event detector for Agent 1
Detects liquidity raids (sweeps of key levels) with quality scoring
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import (
    INSTRUMENT,
    LIQUIDITY_QUALITY,
    LIQUIDITY_WEIGHTS,
    HOLD_BONUSES
)


class LiquidityEventDetector:
    """Detects and scores liquidity events (raids of key levels)"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize detector

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument

    def detect_events(
        self,
        ohlc_df: pd.DataFrame,
        reference_levels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect liquidity events in recent data

        Args:
            ohlc_df: DataFrame with OHLC data
            reference_levels: List of reference level records

        Returns:
            List of liquidity event records
        """
        if ohlc_df is None or ohlc_df.empty or not reference_levels:
            logger.warning("Insufficient data for liquidity event detection")
            return []

        events = []
        now = tz_manager.now_utc()

        # Look back 4 hours for recent events
        lookback_start = now - timedelta(hours=4)

        df_copy = ohlc_df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

        # Filter to recent data
        recent_df = df_copy[df_copy['timestamp'] >= lookback_start]

        if recent_df.empty:
            return []

        try:
            # Check each reference level for raids
            for level in reference_levels:
                level_type = level.get('level_type')
                level_price = level.get('price')

                if not level_type or level_price is None:
                    continue

                # Check for raids (price sweeping through level)
                raid = self._detect_raid(recent_df, level_price, level_type)

                if raid:
                    # Determine event type from level type
                    event_type = self._get_event_type(level_type)

                    # Create event record
                    event = self._create_event_record(
                        raid['timestamp'],
                        event_type,
                        raid['direction'],
                        level_price,
                        raid['sweep_price'],
                        raid['quality_score'],
                        raid['hold_bonus'],
                        now
                    )
                    events.append(event)

            logger.info(f"Detected {len(events)} liquidity events")
            return events

        except Exception as e:
            logger.error(f"Error detecting liquidity events: {str(e)}")
            return []

    def _detect_raid(
        self,
        df: pd.DataFrame,
        level_price: float,
        level_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if level was raided (swept)

        Args:
            df: OHLC DataFrame
            level_price: Price level to check
            level_type: Type of level

        Returns:
            Dict with raid details or None
        """
        # Find bars that touched or crossed the level
        tolerance = 0.5  # Price tolerance in points

        # Check for bullish raid (sweep below level)
        bullish_sweep = df[df['low'] <= (level_price - tolerance)]
        if not bullish_sweep.empty:
            # Get the lowest sweep
            idx = bullish_sweep['low'].idxmin()
            sweep_bar = bullish_sweep.loc[idx]

            # Quality scoring
            quality = self._assess_quality(sweep_bar, level_price, "BULLISH")

            # Hold confirmation
            hold_bonus = self._assess_hold(df, sweep_bar['timestamp'], level_price, "BULLISH")

            return {
                'timestamp': sweep_bar['timestamp'],
                'direction': "BULLISH",
                'sweep_price': float(sweep_bar['low']),
                'quality_score': quality,
                'hold_bonus': hold_bonus,
            }

        # Check for bearish raid (sweep above level)
        bearish_sweep = df[df['high'] >= (level_price + tolerance)]
        if not bearish_sweep.empty:
            # Get the highest sweep
            idx = bearish_sweep['high'].idxmax()
            sweep_bar = bearish_sweep.loc[idx]

            # Quality scoring
            quality = self._assess_quality(sweep_bar, level_price, "BEARISH")

            # Hold confirmation
            hold_bonus = self._assess_hold(df, sweep_bar['timestamp'], level_price, "BEARISH")

            return {
                'timestamp': sweep_bar['timestamp'],
                'direction': "BEARISH",
                'sweep_price': float(sweep_bar['high']),
                'quality_score': quality,
                'hold_bonus': hold_bonus,
            }

        return None

    def _assess_quality(self, sweep_bar: pd.Series, level_price: float, direction: str) -> float:
        """
        Assess sweep quality (clean sweep, wick, near miss)

        Args:
            sweep_bar: Bar that swept the level
            level_price: Level price
            direction: BULLISH or BEARISH

        Returns:
            Quality score (0.4 - 1.0)
        """
        if direction == "BULLISH":
            # Check if close is below level (clean sweep)
            if sweep_bar['close'] < level_price:
                return LIQUIDITY_QUALITY['CLEAN_SWEEP']
            # Check if it's a wick (low touched but close above)
            elif sweep_bar['low'] < level_price < sweep_bar['close']:
                return LIQUIDITY_QUALITY['WICK']
            else:
                return LIQUIDITY_QUALITY['NEAR_MISS']
        else:  # BEARISH
            # Check if close is above level (clean sweep)
            if sweep_bar['close'] > level_price:
                return LIQUIDITY_QUALITY['CLEAN_SWEEP']
            # Check if it's a wick (high touched but close below)
            elif sweep_bar['high'] > level_price > sweep_bar['close']:
                return LIQUIDITY_QUALITY['WICK']
            else:
                return LIQUIDITY_QUALITY['NEAR_MISS']

    def _assess_hold(
        self,
        df: pd.DataFrame,
        sweep_time: datetime,
        level_price: float,
        direction: str
    ) -> float:
        """
        Assess hold time after sweep

        Args:
            df: OHLC DataFrame
            sweep_time: Time of sweep
            level_price: Level price
            direction: BULLISH or BEARISH

        Returns:
            Hold bonus (0.0 - 0.20)
        """
        # Get bars after sweep
        after_sweep = df[df['timestamp'] > sweep_time]

        if after_sweep.empty:
            return 0.0

        # Count minutes held
        held_bars = 0

        for idx, bar in after_sweep.iterrows():
            if direction == "BULLISH":
                # Check if price stayed below level
                if bar['high'] < level_price:
                    held_bars += 1
                else:
                    break
            else:  # BEARISH
                # Check if price stayed above level
                if bar['low'] > level_price:
                    held_bars += 1
                else:
                    break

        # Calculate hold time in minutes (assuming 1-minute bars)
        hold_minutes = held_bars

        # Assign bonus
        if hold_minutes >= 120:  # > 2 hours
            return HOLD_BONUSES['LONG']
        elif hold_minutes >= 60:  # 1-2 hours
            return HOLD_BONUSES['MEDIUM']
        elif hold_minutes >= 30:  # 30min-1hr
            return HOLD_BONUSES['SHORT']
        else:
            return 0.0

    def _get_event_type(self, level_type: str) -> str:
        """
        Map level type to event type

        Args:
            level_type: Reference level type

        Returns:
            Event type string
        """
        mapping = {
            'ASIAN_HIGH': 'ASIA_RANGE',
            'ASIAN_LOW': 'ASIA_RANGE',
            'PREV_DAY_HIGH': 'PREV_DAY_HL',
            'PREV_DAY_LOW': 'PREV_DAY_HL',
            'WEEKLY_OPEN': 'SESSION_HL',
            'DAILY_OPEN': 'SESSION_HL',
            'NY_OPEN': 'SESSION_HL',
            '4H_OPEN': 'SESSION_HL',
            '1H_OPEN': 'SESSION_HL',
            'MONTHLY_OPEN': 'SESSION_HL',
        }

        return mapping.get(level_type, 'SESSION_HL')

    def _create_event_record(
        self,
        timestamp: datetime,
        event_type: str,
        direction: str,
        level_price: float,
        sweep_price: float,
        quality_score: float,
        hold_bonus: float,
        detected_at: datetime
    ) -> Dict[str, Any]:
        """
        Create a liquidity event record for database insertion

        Args:
            timestamp: Time of the event
            event_type: Type of event (ASIA_RANGE, PREV_DAY_HL, etc.)
            direction: BULLISH or BEARISH
            level_price: Original level price
            sweep_price: Actual sweep price
            quality_score: Quality score (0.4-1.0)
            hold_bonus: Hold bonus (0.0-0.20)
            detected_at: Detection timestamp

        Returns:
            Dict record for database
        """
        # Get event weight
        weight = LIQUIDITY_WEIGHTS.get(event_type, 1.0)

        return {
            "instrument": self.instrument,
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "event_type": event_type,
            "direction": direction,
            "level_price": round(level_price, 2),
            "sweep_price": round(sweep_price, 2),
            "quality_score": round(quality_score, 2),
            "hold_confirmed": hold_bonus > 0,
            "event_weight": round(weight, 2),
        }


# Global instance
liquidity_detector = LiquidityEventDetector()
