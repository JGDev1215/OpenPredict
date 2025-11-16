"""
Integration tests for Agent 1
Tests the full data collection pipeline
"""
import unittest
from datetime import datetime
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculators.reference_level_calculator import ReferenceLevelCalculator
from calculators.fibonacci_pivot_calculator import FibonacciPivotCalculator
from calculators.hourly_block_segmenter import HourlyBlockSegmenter
from calculators.fvg_detector import FVGDetector


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline"""

    def setUp(self):
        """Set up test fixtures"""
        # Create realistic sample data
        timestamps = pd.date_range(start='2025-01-15 00:00:00', periods=2880, freq='1min')
        self.sample_df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0 + i * 0.1 for i in range(2880)],
            'high': [17005.0 + i * 0.1 for i in range(2880)],
            'low': [16995.0 + i * 0.1 for i in range(2880)],
            'close': [17002.0 + i * 0.1 for i in range(2880)],
            'volume': [1000 for _ in range(2880)],
        })

    def test_full_pipeline(self):
        """Test that all calculators work together"""

        # Reference levels
        ref_calc = ReferenceLevelCalculator()
        ref_levels = ref_calc.calculate_all_levels(self.sample_df)
        self.assertIsInstance(ref_levels, list)

        # Fibonacci pivots
        fib_calc = FibonacciPivotCalculator()
        pivots = fib_calc.calculate_pivots(self.sample_df)
        self.assertIsInstance(pivots, list)

        # Hourly blocks
        block_seg = HourlyBlockSegmenter()
        blocks = block_seg.segment_current_hour(self.sample_df)
        self.assertIsInstance(blocks, list)

        # FVG detector
        fvg_det = FVGDetector()
        fvgs = fvg_det.detect_fvg(self.sample_df)
        self.assertIsInstance(fvgs, list)

        # All should complete without errors
        self.assertTrue(True)

    def test_data_consistency(self):
        """Test that all records have consistent structure"""

        ref_calc = ReferenceLevelCalculator()
        ref_levels = ref_calc.calculate_all_levels(self.sample_df)

        # All records should have same keys
        if ref_levels:
            keys = set(ref_levels[0].keys())
            for level in ref_levels:
                self.assertEqual(set(level.keys()), keys)


if __name__ == '__main__':
    unittest.main()
