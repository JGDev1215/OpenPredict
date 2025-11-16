"""
Edge case tests for Agent 1 Data Collector
Tests boundary conditions, error scenarios, and data quality issues
"""
import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from calculators.reference_level_calculator import ReferenceLevelCalculator
from calculators.fibonacci_pivot_calculator import FibonacciPivotCalculator
from calculators.liquidity_event_detector import LiquidityEventDetector
from calculators.fvg_detector import FVGDetector
from calculators.hourly_block_segmenter import HourlyBlockSegmenter
from calculators.market_structure_detector import MarketStructureDetector


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for all calculators"""

    def setUp(self):
        """Set up test fixtures"""
        self.ref_calc = ReferenceLevelCalculator()
        self.fib_calc = FibonacciPivotCalculator()
        self.liq_detector = LiquidityEventDetector()
        self.fvg_detector = FVGDetector()
        self.block_seg = HourlyBlockSegmenter()
        self.structure_detector = MarketStructureDetector()

    # ========== DATA QUALITY TESTS ==========

    def test_empty_dataframe_all_calculators(self):
        """Test all calculators handle empty DataFrame gracefully"""
        empty_df = pd.DataFrame()

        # Reference levels
        ref_levels = self.ref_calc.calculate_all_levels(empty_df)
        self.assertIsInstance(ref_levels, list)
        self.assertEqual(len(ref_levels), 0)

        # Fibonacci pivots
        pivots = self.fib_calc.calculate_pivots(empty_df)
        self.assertIsInstance(pivots, list)
        self.assertEqual(len(pivots), 0)

        # FVG detector
        fvgs = self.fvg_detector.detect_fvg(empty_df)
        self.assertIsInstance(fvgs, list)
        self.assertEqual(len(fvgs), 0)

        # Hourly blocks
        blocks = self.block_seg.segment_current_hour(empty_df)
        self.assertIsInstance(blocks, list)
        self.assertEqual(len(blocks), 0)

    def test_single_bar_input(self):
        """Test calculators with insufficient data (single bar)"""
        single_bar_df = pd.DataFrame({
            'timestamp': [datetime(2025, 1, 15, 9, 30)],
            'open': [17000.0],
            'high': [17010.0],
            'low': [16990.0],
            'close': [17005.0],
            'volume': [1000],
        })

        # Should not crash, may return empty results
        ref_levels = self.ref_calc.calculate_all_levels(single_bar_df)
        self.assertIsInstance(ref_levels, list)

        pivots = self.fib_calc.calculate_pivots(single_bar_df)
        self.assertIsInstance(pivots, list)

        fvgs = self.fvg_detector.detect_fvg(single_bar_df)
        self.assertIsInstance(fvgs, list)

    def test_null_values_in_ohlc(self):
        """Test handling of NULL/NaN values in OHLC data"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17010.0] * 100,
            'low': [16990.0] * 100,
            'close': [17005.0] * 100,
            'volume': [1000] * 100,
        })

        # Insert NaN values
        df.loc[10, 'close'] = np.nan
        df.loc[20, 'high'] = np.nan

        # Calculators should handle NaN values (drop or interpolate)
        # Should not crash
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            self.assertIsInstance(ref_levels, list)
        except Exception as e:
            self.fail(f"Reference level calculator failed with NaN: {e}")

    def test_extreme_price_values(self):
        """Test handling of extreme/outlier price values"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17010.0] * 100,
            'low': [16990.0] * 100,
            'close': [17005.0] * 100,
            'volume': [1000] * 100,
        })

        # Insert extreme outlier (likely data error)
        df.loc[50, 'high'] = 999999.0
        df.loc[50, 'low'] = 0.01

        # Should handle gracefully (may filter outliers)
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            self.assertIsInstance(ref_levels, list)
        except Exception as e:
            self.fail(f"Failed with outliers: {e}")

    def test_duplicate_timestamps(self):
        """Test handling of duplicate timestamps"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=50, freq='1min')
        # Duplicate last 10 timestamps
        timestamps = list(timestamps) + list(timestamps[-10:])

        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 60,
            'high': [17010.0] * 60,
            'low': [16990.0] * 60,
            'close': [17005.0] * 60,
            'volume': [1000] * 60,
        })

        # Should deduplicate or handle gracefully
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            self.assertIsInstance(ref_levels, list)
        except Exception as e:
            self.fail(f"Failed with duplicate timestamps: {e}")

    def test_out_of_order_timestamps(self):
        """Test handling of unsorted timestamps"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        # Shuffle timestamps
        shuffled_timestamps = timestamps.to_list()
        np.random.shuffle(shuffled_timestamps)

        df = pd.DataFrame({
            'timestamp': shuffled_timestamps,
            'open': [17000.0] * 100,
            'high': [17010.0] * 100,
            'low': [16990.0] * 100,
            'close': [17005.0] * 100,
            'volume': [1000] * 100,
        })

        # Calculators should sort by timestamp
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            self.assertIsInstance(ref_levels, list)
        except Exception as e:
            self.fail(f"Failed with unsorted timestamps: {e}")

    def test_zero_volume_bars(self):
        """Test handling of zero volume bars"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17010.0] * 100,
            'low': [16990.0] * 100,
            'close': [17005.0] * 100,
            'volume': [0] * 100,  # All zero volume
        })

        # Should handle gracefully (may skip volume-based calculations)
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            self.assertIsInstance(ref_levels, list)
        except Exception as e:
            self.fail(f"Failed with zero volume: {e}")

    # ========== BOUNDARY CONDITION TESTS ==========

    def test_market_open_transition(self):
        """Test behavior at market open (9:30 AM ET)"""
        # Pre-market data + market open
        timestamps = pd.date_range(start='2025-01-15 09:25', end='2025-01-15 09:35', freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * len(timestamps),
            'high': [17010.0] * len(timestamps),
            'low': [16990.0] * len(timestamps),
            'close': [17005.0] * len(timestamps),
            'volume': [100] * len(timestamps),
        })

        # Should handle market open transition
        ref_levels = self.ref_calc.calculate_all_levels(df)
        self.assertIsInstance(ref_levels, list)

    def test_market_close_transition(self):
        """Test behavior at market close (4:00 PM ET)"""
        timestamps = pd.date_range(start='2025-01-15 15:55', end='2025-01-15 16:05', freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * len(timestamps),
            'high': [17010.0] * len(timestamps),
            'low': [16990.0] * len(timestamps),
            'close': [17005.0] * len(timestamps),
            'volume': [100] * len(timestamps),
        })

        ref_levels = self.ref_calc.calculate_all_levels(df)
        self.assertIsInstance(ref_levels, list)

    def test_weekend_data(self):
        """Test handling of weekend (no trading) data"""
        # Saturday data
        timestamps = pd.date_range(start='2025-01-18 09:30', periods=100, freq='1min')  # Saturday
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17010.0] * 100,
            'low': [16990.0] * 100,
            'close': [17005.0] * 100,
            'volume': [0] * 100,  # No volume on weekend
        })

        # Should handle gracefully
        ref_levels = self.ref_calc.calculate_all_levels(df)
        self.assertIsInstance(ref_levels, list)

    def test_flat_market(self):
        """Test with flat market (no price movement)"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17000.0] * 100,  # No highs
            'low': [17000.0] * 100,   # No lows
            'close': [17000.0] * 100,
            'volume': [1000] * 100,
        })

        # Should handle flat market (may return minimal levels)
        ref_levels = self.ref_calc.calculate_all_levels(df)
        self.assertIsInstance(ref_levels, list)

        fvgs = self.fvg_detector.detect_fvg(df)
        self.assertIsInstance(fvgs, list)
        # No FVG should be detected in flat market
        self.assertEqual(len(fvgs), 0)

    # ========== CALCULATOR-SPECIFIC EDGE CASES ==========

    def test_no_liquidity_events_detected(self):
        """Test when no liquidity events are found"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0 + i * 0.1 for i in range(100)],
            'high': [17001.0 + i * 0.1 for i in range(100)],
            'low': [16999.0 + i * 0.1 for i in range(100)],
            'close': [17000.5 + i * 0.1 for i in range(100)],
            'volume': [1000] * 100,
        })

        ref_levels = []  # No reference levels

        liquidity_events = self.liq_detector.detect_events(df, ref_levels)
        self.assertIsInstance(liquidity_events, list)
        # May be empty
        self.assertEqual(len(liquidity_events), 0)

    def test_no_fvg_patterns(self):
        """Test when no FVG patterns are detected"""
        # Continuous price action (no gaps)
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': [17002.0] * 100,
            'low': [16998.0] * 100,
            'close': [17001.0] * 100,
            'volume': [1000] * 100,
        })

        fvgs = self.fvg_detector.detect_fvg(df)
        self.assertIsInstance(fvgs, list)
        # No FVG expected with continuous price
        self.assertEqual(len(fvgs), 0)

    def test_extreme_volatility(self):
        """Test with extreme volatility (large price swings)"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=100, freq='1min')
        
        # Alternating high volatility
        highs = [17000.0 + (50 if i % 2 == 0 else 0) for i in range(100)]
        lows = [17000.0 - (50 if i % 2 == 1 else 0) for i in range(100)]
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0] * 100,
            'high': highs,
            'low': lows,
            'close': [17000.0] * 100,
            'volume': [10000] * 100,  # High volume
        })

        # Should handle extreme volatility
        try:
            ref_levels = self.ref_calc.calculate_all_levels(df)
            fvgs = self.fvg_detector.detect_fvg(df)
            self.assertIsInstance(ref_levels, list)
            self.assertIsInstance(fvgs, list)
        except Exception as e:
            self.fail(f"Failed with extreme volatility: {e}")


class TestDataConsistency(unittest.TestCase):
    """Test data consistency and record structure"""

    def setUp(self):
        """Set up test fixtures"""
        timestamps = pd.date_range(start='2025-01-15 09:30', periods=500, freq='1min')
        self.df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0 + i * 0.1 for i in range(500)],
            'high': [17005.0 + i * 0.1 for i in range(500)],
            'low': [16995.0 + i * 0.1 for i in range(500)],
            'close': [17002.0 + i * 0.1 for i in range(500)],
            'volume': [1000] * 500,
        })

    def test_reference_levels_structure(self):
        """Test reference level records have consistent structure"""
        calc = ReferenceLevelCalculator()
        levels = calc.calculate_all_levels(self.df)

        if levels:
            required_keys = {'instrument', 'timestamp', 'level_type', 'price'}
            for level in levels:
                self.assertTrue(required_keys.issubset(level.keys()),
                               f"Missing keys in level: {level}")
                self.assertIsInstance(level['price'], (int, float))
                self.assertIsInstance(level['timestamp'], str)

    def test_fibonacci_pivots_structure(self):
        """Test Fibonacci pivot records have consistent structure"""
        calc = FibonacciPivotCalculator()
        pivots = calc.calculate_pivots(self.df)

        if pivots:
            required_keys = {'instrument', 'timestamp', 'period', 'level', 'price'}
            for pivot in pivots:
                self.assertTrue(required_keys.issubset(pivot.keys()),
                               f"Missing keys in pivot: {pivot}")
                self.assertIsInstance(pivot['price'], (int, float))

    def test_fvg_structure(self):
        """Test FVG records have consistent structure"""
        detector = FVGDetector()
        fvgs = detector.detect_fvg(self.df)

        if fvgs:
            required_keys = {'instrument', 'timestamp', 'gap_start', 'gap_end', 'gap_size'}
            for fvg in fvgs:
                self.assertTrue(required_keys.issubset(fvg.keys()),
                               f"Missing keys in FVG: {fvg}")
                self.assertIsInstance(fvg['gap_size'], (int, float))
                self.assertGreater(fvg['gap_size'], 0)


if __name__ == '__main__':
    unittest.main()
