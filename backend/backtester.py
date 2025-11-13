"""
Backtesting system for historical price prediction evaluation
"""
from typing import List
from datetime import datetime, timedelta
import pytz
import uuid
from models import (
    BacktestRequest,
    BacktestResult,
    PredictionResult,
    PredictionDirection,
    AggregatedOHLC
)
from services import SupabaseService, DataAggregator
from backend import PredictionEngine
from config import TIMEZONE, TIMEFRAMES

# Configuration for period filtering
# Minimum data completeness threshold (as decimal, e.g., 0.05 = 5%)
# Lower values allow more sparse data: 0.05 = very permissive, 0.2 = strict, 0.5 = very strict
MIN_DATA_COMPLETENESS = 0.05


class Backtester:
    """
    Backtesting engine for evaluating prediction accuracy on historical data
    """

    def __init__(self):
        """Initialize backtester"""
        self.supabase = SupabaseService()
        self.aggregator = DataAggregator()
        self.engine = PredictionEngine()
        self.timezone = pytz.timezone(TIMEZONE)

    def run_backtest(self, request: BacktestRequest) -> BacktestResult:
        """
        Run backtest on historical data

        Args:
            request: Backtest request parameters

        Returns:
            BacktestResult with complete results
        """
        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")

        # Make timezone-aware
        start_date = self.timezone.localize(start_date.replace(hour=0, minute=0, second=0))
        end_date = self.timezone.localize(end_date.replace(hour=23, minute=59, second=59))

        # Get timeframe duration
        timeframe_minutes = TIMEFRAMES.get(request.timeframe)
        if not timeframe_minutes:
            raise ValueError(f"Invalid timeframe: {request.timeframe}")

        # Generate test ID
        test_id = str(uuid.uuid4())[:8]

        # Fetch historical data
        print(f"Fetching historical data for {request.symbol} from {request.start_date} to {request.end_date}...")
        bars = self.supabase.fetch_aggregated_bars(
            symbol=request.symbol,
            start_time=start_date,
            end_time=end_date,
            bar_size_minutes=request.aggregation_minutes
        )

        if not bars:
            raise ValueError(f"No data found for {request.symbol} in the specified date range")

        # Validate data completeness
        date_range_days = (end_date - start_date).days
        expected_bars_per_day = (24 * 60) // request.aggregation_minutes
        expected_total_bars = date_range_days * expected_bars_per_day
        data_completeness_pct = (len(bars) / expected_total_bars * 100) if expected_total_bars > 0 else 0

        print(f"Fetched {len(bars)} bars. Running backtest...")
        print(f"Data validation: Expected ~{expected_total_bars} bars, got {len(bars)} ({data_completeness_pct:.1f}% coverage)")

        if data_completeness_pct < 80:
            print(f"WARNING: Data coverage is only {data_completeness_pct:.1f}%. This is below 80% - results may be incomplete.")
            print(f"To improve coverage, ensure sufficient data is in Supabase or adjust the date range.")

        # Generate periods to test
        periods = self._generate_test_periods(
            start_date,
            end_date,
            timeframe_minutes,
            request.timeframe
        )

        print(f"Generated {len(periods)} periods for testing")

        # Run predictions for each period
        results: List[PredictionResult] = []

        # Diagnostic counters
        periods_with_no_bars = 0
        periods_insufficient_data = 0
        periods_with_errors = 0

        for i, (period_start, period_end) in enumerate(periods):
            try:
                # Get bars for this period (plus some history for volatility calc)
                lookback_start = period_start - timedelta(hours=1)  # Extra lookback for volatility (optimized from 4h)
                period_bars = [
                    bar for bar in bars
                    if lookback_start <= bar.timestamp < period_end
                ]

                if not period_bars:
                    periods_with_no_bars += 1
                    continue

                # Check data completeness (accept periods with at least MIN_DATA_COMPLETENESS)
                # This allows for sparse data while maintaining analysis quality
                expected_bar_count = timeframe_minutes // request.aggregation_minutes
                actual_bar_count = len([b for b in period_bars if period_start <= b.timestamp < period_end])
                data_completeness = actual_bar_count / expected_bar_count if expected_bar_count > 0 else 0

                if data_completeness < MIN_DATA_COMPLETENESS:
                    # Insufficient data, skip this period
                    periods_insufficient_data += 1
                    continue

                # Run prediction analysis (at 5/7 point)
                analysis = self.engine.analyze_period(
                    bars=period_bars,
                    period_start=period_start,
                    timeframe_minutes=timeframe_minutes
                )

                # Get actual close at 7/7
                actual_bars = [bar for bar in period_bars if period_start <= bar.timestamp < period_end]
                aggregated = self.aggregator.aggregate_bars(
                    bars=actual_bars,
                    timeframe_minutes=timeframe_minutes,
                    period_start=period_start,
                    period_end=period_end
                )

                actual_close = aggregated.close
                actual_direction = aggregated.get_direction()

                # Evaluate prediction
                prediction_correct = (
                    analysis.prediction == actual_direction and
                    actual_direction != PredictionDirection.NEUTRAL
                )

                # Only count non-neutral outcomes in accuracy
                accuracy_contribution = actual_direction != PredictionDirection.NEUTRAL

                result = PredictionResult(
                    analysis=analysis,
                    actual_close=actual_close,
                    actual_direction=actual_direction,
                    prediction_correct=prediction_correct,
                    accuracy_contribution=accuracy_contribution
                )

                results.append(result)

                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(periods)} periods...")

            except Exception as e:
                periods_with_errors += 1
                print(f"Error processing period {period_start}: {str(e)}")
                continue

        # Print diagnostic summary
        print(f"\n=== BACKTEST DIAGNOSTICS ===")
        print(f"Total periods generated: {len(periods)}")
        print(f"Periods with no bars: {periods_with_no_bars}")
        print(f"Periods with insufficient data (<{MIN_DATA_COMPLETENESS*100:.0f}% completeness): {periods_insufficient_data}")
        print(f"Periods with errors: {periods_with_errors}")
        print(f"Periods successfully analyzed: {len(results)}")
        print(f"Data coverage: {len(results)/len(periods)*100:.1f}% of generated periods")
        print(f"===========================\n")

        # Calculate summary statistics
        # Count ALL processed periods (including neutrals) for total prediction count
        total_predictions = len(results)
        # Only count correct predictions that contribute to accuracy (exclude neutrals)
        correct_predictions = sum(1 for r in results if r.prediction_correct and r.accuracy_contribution)
        incorrect_predictions = total_predictions - correct_predictions
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0.0

        # Direction-specific stats
        up_predictions = [r for r in results if r.analysis.prediction == PredictionDirection.UP and r.accuracy_contribution]
        down_predictions = [r for r in results if r.analysis.prediction == PredictionDirection.DOWN and r.accuracy_contribution]
        neutral_predictions = [r for r in results if r.analysis.prediction == PredictionDirection.NEUTRAL]

        up_correct = sum(1 for r in up_predictions if r.prediction_correct)
        down_correct = sum(1 for r in down_predictions if r.prediction_correct)

        up_accuracy = (up_correct / len(up_predictions) * 100) if up_predictions else None
        down_accuracy = (down_correct / len(down_predictions) * 100) if down_predictions else None

        print(f"\nBacktest complete! Accuracy: {accuracy:.2f}%")
        print(f"Total periods: {len(results)}, Predictions: {total_predictions}")

        return BacktestResult(
            test_id=test_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            total_periods=len(results),
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            incorrect_predictions=incorrect_predictions,
            accuracy_percentage=accuracy,
            predictions=results,
            up_predictions=len(up_predictions),
            down_predictions=len(down_predictions),
            neutral_predictions=len(neutral_predictions),
            up_accuracy=up_accuracy,
            down_accuracy=down_accuracy
        )

    def _generate_test_periods(
        self,
        start_date: datetime,
        end_date: datetime,
        timeframe_minutes: int,
        timeframe_name: str
    ) -> List[tuple[datetime, datetime]]:
        """
        Generate list of (period_start, period_end) tuples for testing

        For regular timeframes (2h, 4h), periods are generated 24/7:
        - Every day, including weekends
        - Continuous generation from start_date to end_date at specified intervals

        Expected prediction counts per timeframe:
        - 2h timeframe: 365 days × 12 sessions = ~4,380 predictions/year
        - 4h timeframe: 365 days × 6 sessions = ~2,190 predictions/year
        - 10AM-12PM: ~252 trading days × 1 session = ~252 predictions/year (Mon-Fri only)

        Note: Actual counts may be lower due to:
        - Missing or incomplete data (configurable MIN_DATA_COMPLETENESS threshold)
        - Neutral predictions (excluded from accuracy metrics)
        - First few periods may lack sufficient history for volatility calculation

        Configuration: Adjust MIN_DATA_COMPLETENESS in backtester.py to tune filtering:
        - 0.05 (5%) = very permissive (includes sparse data)
        - 0.20 (20%) = moderate
        - 0.50 (50%) = strict (requires mostly complete data)

        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            timeframe_minutes: Timeframe duration in minutes
            timeframe_name: Timeframe identifier (for special handling)

        Returns:
            List of period tuples (period_start, period_end)
        """
        periods = []

        # Special handling for 10AM-12PM slot
        if timeframe_name == "custom_10am_12pm":
            current_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
            while current_date <= end_date:
                period_start = current_date
                period_end = current_date + timedelta(minutes=timeframe_minutes)

                # Only include trading days (Mon-Fri)
                if period_start.weekday() < 5:  # 0-4 are Mon-Fri
                    periods.append((period_start, period_end))

                current_date += timedelta(days=1)

        else:
            # Regular intervals (2h, 4h) - generate periods 24/7
            current_time = self.aggregator.align_to_timeframe_start(start_date, timeframe_minutes)

            while current_time <= end_date:
                period_start = current_time
                period_end = current_time + timedelta(minutes=timeframe_minutes)
                periods.append((period_start, period_end))
                current_time += timedelta(minutes=timeframe_minutes)

        return periods
