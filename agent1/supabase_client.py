"""
Supabase client for Agent 1
Handles database operations with error logging
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from utils.logger import logger
from config import SUPABASE_URL, SUPABASE_KEY


class SupabaseClient:
    """Manages Supabase database operations"""

    def __init__(self):
        """Initialize Supabase client"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")

    def upsert_ohlc(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert OHLC data to ohlc_data table

        Args:
            data: List of OHLC records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No OHLC data to upsert")
                return True

            response = self.client.table("ohlc_data").upsert(data).execute()
            logger.info(f"Upserted {len(data)} OHLC records")
            return True

        except Exception as e:
            logger.error(f"Error upserting OHLC data: {str(e)}")
            self._log_error("upsert_ohlc", str(e))
            return False

    def upsert_reference_levels(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert reference levels to reference_levels table

        Args:
            data: List of reference level records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No reference levels to upsert")
                return True

            response = self.client.table("reference_levels").upsert(data).execute()
            logger.info(f"Upserted {len(data)} reference level records")
            return True

        except Exception as e:
            logger.error(f"Error upserting reference levels: {str(e)}")
            self._log_error("upsert_reference_levels", str(e))
            return False

    def upsert_fibonacci_pivots(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert Fibonacci pivots to fibonacci_pivots table

        Args:
            data: List of pivot records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No pivots to upsert")
                return True

            response = self.client.table("fibonacci_pivots").upsert(data).execute()
            logger.info(f"Upserted {len(data)} pivot records")
            return True

        except Exception as e:
            logger.error(f"Error upserting pivots: {str(e)}")
            self._log_error("upsert_fibonacci_pivots", str(e))
            return False

    def upsert_liquidity_events(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert liquidity events to liquidity_events table

        Args:
            data: List of liquidity event records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No liquidity events to upsert")
                return True

            response = self.client.table("liquidity_events").upsert(data).execute()
            logger.info(f"Upserted {len(data)} liquidity event records")
            return True

        except Exception as e:
            logger.error(f"Error upserting liquidity events: {str(e)}")
            self._log_error("upsert_liquidity_events", str(e))
            return False

    def upsert_market_structure(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert market structure to market_structure table

        Args:
            data: List of structure records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No market structure to upsert")
                return True

            response = self.client.table("market_structure").upsert(data).execute()
            logger.info(f"Upserted {len(data)} market structure records")
            return True

        except Exception as e:
            logger.error(f"Error upserting market structure: {str(e)}")
            self._log_error("upsert_market_structure", str(e))
            return False

    def upsert_fvg(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert Fair Value Gaps to fvg table

        Args:
            data: List of FVG records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No FVG data to upsert")
                return True

            response = self.client.table("fvg").upsert(data).execute()
            logger.info(f"Upserted {len(data)} FVG records")
            return True

        except Exception as e:
            logger.error(f"Error upserting FVG: {str(e)}")
            self._log_error("upsert_fvg", str(e))
            return False

    def upsert_hourly_blocks(self, data: List[Dict[str, Any]]) -> bool:
        """
        Upsert hourly blocks to hourly_blocks table

        Args:
            data: List of hourly block records

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No hourly blocks to upsert")
                return True

            response = self.client.table("hourly_blocks").upsert(data).execute()
            logger.info(f"Upserted {len(data)} hourly block records")
            return True

        except Exception as e:
            logger.error(f"Error upserting hourly blocks: {str(e)}")
            self._log_error("upsert_hourly_blocks", str(e))
            return False

    def _log_error(self, operation: str, error_message: str):
        """
        Log error to error_log table

        Args:
            operation: Operation that failed
            error_message: Error message
        """
        try:
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "component": "agent1",
                "operation": operation,
                "error_message": error_message,
                "severity": "ERROR",
            }
            self.client.table("error_log").insert(error_data).execute()

        except Exception as e:
            logger.error(f"Failed to log error to database: {str(e)}")

    def get_latest_ohlc(self, instrument: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Get latest OHLC records

        Args:
            instrument: Trading instrument
            limit: Number of records to fetch

        Returns:
            List of OHLC records or None
        """
        try:
            response = (
                self.client.table("ohlc_data")
                .select("*")
                .eq("instrument", instrument)
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data

        except Exception as e:
            logger.error(f"Error fetching latest OHLC: {str(e)}")
            return None

    def get_reference_levels(self, instrument: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get latest reference levels

        Args:
            instrument: Trading instrument

        Returns:
            List of reference level records or None
        """
        try:
            response = (
                self.client.table("reference_levels")
                .select("*")
                .eq("instrument", instrument)
                .order("timestamp", desc=True)
                .limit(10)
                .execute()
            )
            return response.data

        except Exception as e:
            logger.error(f"Error fetching reference levels: {str(e)}")
            return None


# Global instance
db_client = SupabaseClient()
