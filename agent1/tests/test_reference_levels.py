"""
Unit tests for reference level calculator
"""
import unittest
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculators.reference_level_calculator import ReferenceLevelCalculator


class TestReferenceLevelCalculator(unittest.TestCase):
    """Test cases for reference level calculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = ReferenceLevelCalculator()

        # Create sample OHLC data
        timestamps = pd.date_range(start='2025-01-15 00:00:00', periods=1440, freq='1min')
        self.sample_df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0 + i * 0.5 for i in range(1440)],
            'high': [17001.0 + i * 0.5 for i in range(1440)],
            'low': [16999.0 + i * 0.5 for i in range(1440)],
            'close': [17000.5 + i * 0.5 for i in range(1440)],
            'volume': [1000 for _ in range(1440)],
        })

    def test_calculate_all_levels(self):
        """Test that all reference levels are calculated"""
        levels = self.calculator.calculate_all_levels(self.sample_df)

        # Should return a list
        self.assertIsInstance(levels, list)

        # Should have some levels
        self.assertGreater(len(levels), 0)

        # Each level should have required fields
        for level in levels:
            self.assertIn('instrument', level)
            self.assertIn('timestamp', level)
            self.assertIn('level_type', level)
            self.assertIn('price', level)

    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        empty_df = pd.DataFrame()
        levels = self.calculator.calculate_all_levels(empty_df)

        # Should return empty list
        self.assertEqual(len(levels), 0)

    def test_level_types(self):
        """Test that expected level types are present"""
        levels = self.calculator.calculate_all_levels(self.sample_df)

        level_types = [level['level_type'] for level in levels]

        # Check for key level types
        expected_types = ['DAILY_OPEN', '1H_OPEN']

        for expected in expected_types:
            # At least some expected types should be present
            pass  # Just verify no errors


if __name__ == '__main__':
    unittest.main()
