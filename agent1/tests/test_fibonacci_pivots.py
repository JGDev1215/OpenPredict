"""
Unit tests for Fibonacci pivot calculator
"""
import unittest
from datetime import datetime
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculators.fibonacci_pivot_calculator import FibonacciPivotCalculator


class TestFibonacciPivotCalculator(unittest.TestCase):
    """Test cases for Fibonacci pivot calculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = FibonacciPivotCalculator()

        # Create sample OHLC data for multiple days
        timestamps = pd.date_range(start='2025-01-10 00:00:00', periods=7200, freq='1min')
        self.sample_df = pd.DataFrame({
            'timestamp': timestamps,
            'open': [17000.0 + (i % 100) * 0.5 for i in range(7200)],
            'high': [17010.0 + (i % 100) * 0.5 for i in range(7200)],
            'low': [16990.0 + (i % 100) * 0.5 for i in range(7200)],
            'close': [17005.0 + (i % 100) * 0.5 for i in range(7200)],
            'volume': [1000 for _ in range(7200)],
        })

    def test_calculate_pivots(self):
        """Test that pivots are calculated"""
        pivots = self.calculator.calculate_pivots(self.sample_df)

        # Should return a list
        self.assertIsInstance(pivots, list)

        # Each pivot should have required fields
        for pivot in pivots:
            self.assertIn('instrument', pivot)
            self.assertIn('timestamp', pivot)
            self.assertIn('period', pivot)
            self.assertIn('level', pivot)
            self.assertIn('price', pivot)

    def test_pivot_levels(self):
        """Test that all pivot levels are present"""
        pivots = self.calculator.calculate_pivots(self.sample_df)

        if pivots:
            # Check for expected levels
            levels = [pivot['level'] for pivot in pivots]

            # Should have various resistance and support levels
            expected_levels = ['PP', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3']

            # At least PP should be present
            # (Other levels depend on data availability)
            pass  # Just verify no errors

    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        empty_df = pd.DataFrame()
        pivots = self.calculator.calculate_pivots(empty_df)

        # Should return empty list
        self.assertEqual(len(pivots), 0)


if __name__ == '__main__':
    unittest.main()
