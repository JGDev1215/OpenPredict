"""
Agent 1 - Data Collector Main Entry Point
Orchestrates data fetching and calculation of all ICT reference levels
Runs every 60 seconds using APScheduler
"""
import sys
import signal
from datetime import datetime
import time
from typing import Optional
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import modules
from yahoo_finance_fetcher import fetcher
from supabase_client import db_client
from calculators.reference_level_calculator import ref_calculator
from calculators.fibonacci_pivot_calculator import fib_calculator
from calculators.liquidity_event_detector import liquidity_detector
from calculators.fvg_detector import fvg_detector
from calculators.hourly_block_segmenter import block_segmenter
from calculators.market_structure_detector import structure_detector
from utils.logger import logger
from utils.market_hours_checker import market_checker
from config import FETCH_INTERVAL_SECONDS, INSTRUMENT


class Agent1:
    """Main Agent 1 class that orchestrates data collection"""

    def __init__(self):
        """Initialize Agent 1"""
        self.scheduler: Optional[BlockingScheduler] = None
        self.is_running = False
        self.execution_count = 0
        self.error_count = 0
        logger.info("Agent 1 initialized")

    def run_collection_cycle(self):
        """
        Execute one collection cycle
        This is the main function called every 60 seconds
        """
        start_time = time.time()
        self.execution_count += 1

        logger.info(f"=== Agent 1 Cycle #{self.execution_count} Started ===")

        try:
            # Step 1: Fetch OHLC data from Yahoo Finance
            logger.info("Step 1: Fetching OHLC data...")
            ohlc_df = fetcher.fetch_ohlc(period="5d", interval="1m", use_cache=False)

            if ohlc_df is None or ohlc_df.empty:
                logger.error("Failed to fetch OHLC data, skipping cycle")
                self.error_count += 1
                return

            logger.info(f"Fetched {len(ohlc_df)} OHLC bars")

            # Step 2: Store OHLC data to database
            logger.info("Step 2: Storing OHLC data to database...")
            ohlc_records = self._prepare_ohlc_records(ohlc_df)
            if ohlc_records:
                success = db_client.upsert_ohlc(ohlc_records)
                if not success:
                    logger.warning("Failed to store OHLC data")

            # Step 3: Calculate reference levels
            logger.info("Step 3: Calculating reference levels...")
            ref_levels = ref_calculator.calculate_all_levels(ohlc_df)
            if ref_levels:
                success = db_client.upsert_reference_levels(ref_levels)
                if success:
                    logger.info(f"Stored {len(ref_levels)} reference levels")

            # Step 4: Calculate Fibonacci pivots
            logger.info("Step 4: Calculating Fibonacci pivots...")
            pivots = fib_calculator.calculate_pivots(ohlc_df)
            if pivots:
                success = db_client.upsert_fibonacci_pivots(pivots)
                if success:
                    logger.info(f"Stored {len(pivots)} pivot points")

            # Step 5: Detect liquidity events
            logger.info("Step 5: Detecting liquidity events...")
            if ref_levels:
                liquidity_events = liquidity_detector.detect_events(ohlc_df, ref_levels)
                if liquidity_events:
                    success = db_client.upsert_liquidity_events(liquidity_events)
                    if success:
                        logger.info(f"Stored {len(liquidity_events)} liquidity events")

            # Step 6: Detect Fair Value Gaps
            logger.info("Step 6: Detecting Fair Value Gaps...")
            fvgs = fvg_detector.detect_fvg(ohlc_df)
            if fvgs:
                success = db_client.upsert_fvg(fvgs)
                if success:
                    logger.info(f"Stored {len(fvgs)} FVG patterns")

            # Step 7: Segment hourly blocks
            logger.info("Step 7: Segmenting hourly blocks...")
            blocks = block_segmenter.segment_recent_hours(ohlc_df, hours=4)
            if blocks:
                success = db_client.upsert_hourly_blocks(blocks)
                if success:
                    logger.info(f"Stored {len(blocks)} hourly blocks")

            # Step 8: Detect market structure
            logger.info("Step 8: Detecting market structure...")
            structure = structure_detector.detect_structure(ohlc_df, timeframes=["15min", "1H", "4H"])
            if structure:
                success = db_client.upsert_market_structure(structure)
                if success:
                    logger.info(f"Stored {len(structure)} structure breaks")

            # Calculate execution time
            execution_time = time.time() - start_time

            logger.info(f"=== Agent 1 Cycle #{self.execution_count} Completed in {execution_time:.2f}s ===")

            # Check if execution time is within target (<8s)
            if execution_time > 8:
                logger.warning(f"Execution time ({execution_time:.2f}s) exceeded 8s target")

        except Exception as e:
            logger.error(f"Error in collection cycle: {str(e)}", exc_info=True)
            self.error_count += 1

    def _prepare_ohlc_records(self, ohlc_df) -> list:
        """
        Convert OHLC DataFrame to database records

        Args:
            ohlc_df: OHLC DataFrame

        Returns:
            List of records for database insertion
        """
        records = []

        # Only insert recent data (last 100 bars) to avoid duplicates
        recent_df = ohlc_df.tail(100)

        for _, row in recent_df.iterrows():
            record = {
                "instrument": INSTRUMENT,
                "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                "open": round(float(row['open']), 2),
                "high": round(float(row['high']), 2),
                "low": round(float(row['low']), 2),
                "close": round(float(row['close']), 2),
                "volume": int(row['volume']),
            }
            records.append(record)

        return records

    def start(self):
        """Start the Agent 1 scheduler"""
        logger.info("Starting Agent 1 Data Collector...")

        # Create scheduler
        self.scheduler = BlockingScheduler()

        # Add job: run every FETCH_INTERVAL_SECONDS
        self.scheduler.add_job(
            func=self.run_collection_cycle,
            trigger=IntervalTrigger(seconds=FETCH_INTERVAL_SECONDS),
            id='data_collection',
            name='Data Collection Cycle',
            replace_existing=True,
        )

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.is_running = True

        logger.info(f"Agent 1 scheduled to run every {FETCH_INTERVAL_SECONDS} seconds")
        logger.info("Agent 1 is now running. Press Ctrl+C to stop.")

        # Run first cycle immediately
        logger.info("Running initial collection cycle...")
        self.run_collection_cycle()

        # Start scheduler
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def stop(self):
        """Stop the Agent 1 scheduler"""
        logger.info("Stopping Agent 1...")

        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)

        self.is_running = False

        logger.info(f"Agent 1 stopped after {self.execution_count} cycles ({self.error_count} errors)")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def get_status(self) -> dict:
        """
        Get Agent 1 status

        Returns:
            Dict with status information
        """
        return {
            "is_running": self.is_running,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "success_rate": round((self.execution_count - self.error_count) / max(self.execution_count, 1) * 100, 2),
        }


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("OpenPredict - Agent 1 Data Collector")
    logger.info("=" * 60)

    # Check market status (optional - Agent 1 can run 24/7)
    if market_checker.is_market_open():
        logger.info("Market is OPEN")
    else:
        logger.info("Market is CLOSED (Agent 1 will still collect data)")

    # Create and start Agent 1
    agent = Agent1()
    agent.start()


if __name__ == "__main__":
    main()
