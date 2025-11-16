"""
Hourly block segmenter for Agent 1
Divides each hour into 7 blocks (~8.57 minutes each) for ICT block analysis
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from utils.logger import logger
from utils.timezone_manager import tz_manager
from config import INSTRUMENT, BLOCKS_PER_HOUR, BLOCK_DURATION_MINUTES


class HourlyBlockSegmenter:
    """Segments hours into 7 blocks for ICT analysis"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize segmenter

        Args:
            instrument: Trading instrument symbol
        """
        self.instrument = instrument
        self.blocks_per_hour = BLOCKS_PER_HOUR
        self.block_duration = BLOCK_DURATION_MINUTES

    def segment_current_hour(self, ohlc_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Segment current hour into blocks

        Args:
            ohlc_df: DataFrame with 1-minute OHLC data

        Returns:
            List of block records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for block segmentation")
            return []

        try:
            now = tz_manager.now_utc()

            # Get current hour start
            hour_start = now.replace(minute=0, second=0, microsecond=0)

            # Generate blocks for current hour
            blocks = self._generate_blocks(ohlc_df, hour_start)

            logger.info(f"Generated {len(blocks)} blocks for hour starting {hour_start}")
            return blocks

        except Exception as e:
            logger.error(f"Error segmenting hour into blocks: {str(e)}")
            return []

    def segment_recent_hours(self, ohlc_df: pd.DataFrame, hours: int = 4) -> List[Dict[str, Any]]:
        """
        Segment recent hours into blocks

        Args:
            ohlc_df: DataFrame with 1-minute OHLC data
            hours: Number of recent hours to segment

        Returns:
            List of block records
        """
        if ohlc_df is None or ohlc_df.empty:
            logger.warning("No OHLC data provided for block segmentation")
            return []

        try:
            now = tz_manager.now_utc()
            all_blocks = []

            # Segment each of the recent hours
            for h in range(hours):
                hour_start = (now - timedelta(hours=h)).replace(minute=0, second=0, microsecond=0)
                blocks = self._generate_blocks(ohlc_df, hour_start)
                all_blocks.extend(blocks)

            logger.info(f"Generated {len(all_blocks)} blocks for {hours} recent hours")
            return all_blocks

        except Exception as e:
            logger.error(f"Error segmenting recent hours: {str(e)}")
            return []

    def _generate_blocks(self, df: pd.DataFrame, hour_start: datetime) -> List[Dict[str, Any]]:
        """
        Generate 7 blocks for a specific hour

        Args:
            df: OHLC DataFrame
            hour_start: Start of the hour

        Returns:
            List of block records
        """
        blocks = []
        hour_end = hour_start + timedelta(hours=1)

        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])

        # Get hour data
        mask = (df_copy['timestamp'] >= hour_start) & (df_copy['timestamp'] < hour_end)
        hour_df = df_copy[mask]

        if hour_df.empty:
            logger.debug(f"No data for hour starting {hour_start}")
            return []

        # Get hour open price
        hour_open = float(hour_df.iloc[0]['open'])

        # Generate 7 blocks
        for block_num in range(1, self.blocks_per_hour + 1):
            block = self._create_block(hour_df, hour_start, hour_open, block_num)
            if block:
                blocks.append(block)

        return blocks

    def _create_block(
        self,
        hour_df: pd.DataFrame,
        hour_start: datetime,
        hour_open: float,
        block_num: int
    ) -> Optional[Dict[str, Any]]:
        """
        Create a single block

        Args:
            hour_df: Hour OHLC data
            hour_start: Start of hour
            hour_open: Hour open price
            block_num: Block number (1-7)

        Returns:
            Block record or None
        """
        # Calculate block time range
        block_start_offset = (block_num - 1) * self.block_duration
        block_end_offset = block_num * self.block_duration

        block_start = hour_start + timedelta(minutes=block_start_offset)
        block_end = hour_start + timedelta(minutes=block_end_offset)

        # Filter to block data
        mask = (hour_df['timestamp'] >= block_start) & (hour_df['timestamp'] < block_end)
        block_df = hour_df[mask]

        if block_df.empty:
            # Block has no data yet (future block)
            return None

        # Calculate block OHLC
        block_open = float(block_df.iloc[0]['open'])
        block_high = float(block_df['high'].max())
        block_low = float(block_df['low'].min())
        block_close = float(block_df.iloc[-1]['close'])
        block_volume = int(block_df['volume'].sum())

        # Calculate deviation from hour open
        deviation = block_close - hour_open

        # Determine bias
        if deviation > 0.5:  # More than 0.5 points above hour open
            bias = "BULLISH"
        elif deviation < -0.5:  # More than 0.5 points below hour open
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        # Calculate volatility score (range relative to open)
        block_range = block_high - block_low
        volatility = round(block_range, 2)

        return {
            "instrument": self.instrument,
            "timestamp": block_start.isoformat(),
            "hour_start": hour_start.isoformat(),
            "block_number": block_num,
            "open": round(block_open, 2),
            "high": round(block_high, 2),
            "low": round(block_low, 2),
            "close": round(block_close, 2),
            "volume": block_volume,
            "deviation_from_hour_open": round(deviation, 2),
            "bias": bias,
            "volatility_score": volatility,
        }


# Global instance
block_segmenter = HourlyBlockSegmenter()
