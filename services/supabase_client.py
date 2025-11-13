"""
Supabase client for fetching OHLC data
"""
from supabase import create_client, Client
from typing import List, Optional
from datetime import datetime, timedelta
import pytz
from config import SUPABASE_URL, SUPABASE_KEY, TIMEZONE
from models import OHLCBar


class SupabaseService:
    """Service for interacting with Supabase"""

    def __init__(self):
        """Initialize Supabase client"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.timezone = pytz.timezone(TIMEZONE)

    def fetch_ohlc_bars(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        table_name: str = "ohlc_3min"
    ) -> List[OHLCBar]:
        """
        Fetch OHLC bars from Supabase for a given time range with pagination
        to bypass the 1000-row default limit.

        Args:
            symbol: Asset symbol (e.g., ES=F, AAPL)
            start_time: Start datetime (timezone-aware)
            end_time: End datetime (timezone-aware)
            table_name: Supabase table name (default: ohlc_3min)

        Returns:
            List of OHLCBar objects
        """
        # Convert to UTC for Supabase query (assuming Supabase stores in UTC)
        start_utc = start_time.astimezone(pytz.UTC)
        end_utc = end_time.astimezone(pytz.UTC)

        try:
            bars = []
            offset = 0
            batch_size = 1000
            total_fetched = 0

            while True:
                # Query Supabase with pagination using .range()
                response = (
                    self.client
                    .table(table_name)
                    .select("*")
                    .eq("symbol", symbol)
                    .gte("timestamp", start_utc.isoformat())
                    .lte("timestamp", end_utc.isoformat())
                    .order("timestamp", desc=False)
                    .range(offset, offset + batch_size - 1)
                    .execute()
                )

                if not response.data:
                    break

                # Convert to OHLCBar objects
                for row in response.data:
                    # Parse timestamp and convert to ET
                    timestamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                    timestamp_et = timestamp.astimezone(self.timezone)

                    bar = OHLCBar(
                        timestamp=timestamp_et,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        symbol=row["symbol"]
                    )
                    bars.append(bar)

                total_fetched += len(response.data)

                # If fewer rows than batch_size, we've reached the end
                if len(response.data) < batch_size:
                    break

                offset += batch_size

            print(f"Fetched {total_fetched} bars for {symbol} from {table_name}")
            return bars

        except Exception as e:
            raise Exception(f"Error fetching data from Supabase: {str(e)}")

    def fetch_aggregated_bars(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        bar_size_minutes: int
    ) -> List[OHLCBar]:
        """
        Fetch pre-aggregated bars if available (e.g., 2min, 5min, 15min, 30min, 1hour tables)
        Falls back to next available granularity if requested table doesn't exist

        Args:
            symbol: Asset symbol
            start_time: Start datetime (timezone-aware)
            end_time: End datetime (timezone-aware)
            bar_size_minutes: Desired bar size (2, 5, 15, 30, 60)

        Returns:
            List of OHLCBar objects
        """
        # Map bar sizes to potential table names
        table_map = {
            2: "ohlc_2min",
            3: "ohlc_3min",
            5: "ohlc_5min",
            15: "ohlc_15min",
            30: "ohlc_30min",
            60: "ohlc_1hour"
        }

        table_name = table_map.get(bar_size_minutes, "ohlc_15min")

        try:
            return self.fetch_ohlc_bars(symbol, start_time, end_time, table_name)
        except Exception as e:
            # Fallback strategy: try next coarser granularity
            print(f"Warning: Could not fetch {bar_size_minutes}min data from {table_name}: {e}")

            # Fallback order: 2min -> 5min -> 15min -> 30min -> 1hour
            fallback_tables = [
                ("ohlc_2min", 2),
                ("ohlc_5min", 5),
                ("ohlc_15min", 15),
                ("ohlc_30min", 30),
                ("ohlc_1hour", 60),
                ("ohlc_3min", 3)  # Last resort
            ]

            for fallback_table, fallback_size in fallback_tables:
                if fallback_table == table_name:
                    continue  # Skip the one we just tried
                try:
                    print(f"Attempting fallback to {fallback_table}...")
                    return self.fetch_ohlc_bars(symbol, start_time, end_time, fallback_table)
                except Exception as fallback_e:
                    continue

            raise Exception(f"Could not fetch data for {symbol} from any available table")

    def get_latest_bar(self, symbol: str, table_name: str = "ohlc_3min") -> Optional[OHLCBar]:
        """
        Get the most recent bar for a symbol

        Args:
            symbol: Asset symbol
            table_name: Supabase table name

        Returns:
            Latest OHLCBar or None
        """
        try:
            response = (
                self.client
                .table(table_name)
                .select("*")
                .eq("symbol", symbol)
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )

            if not response.data:
                return None

            row = response.data[0]
            timestamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            timestamp_et = timestamp.astimezone(self.timezone)

            return OHLCBar(
                timestamp=timestamp_et,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                symbol=row["symbol"]
            )

        except Exception as e:
            raise Exception(f"Error fetching latest bar: {str(e)}")
