"""
Yahoo Finance data fetcher for Agent 1
Fetches OHLC data with retry logic and caching
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
import yfinance as yf
from utils.logger import logger
from config import (
    INSTRUMENT,
    YFINANCE_RETRY_ATTEMPTS,
    YFINANCE_RETRY_DELAY,
    YFINANCE_CACHE_TTL
)


class YahooFinanceFetcher:
    """Fetches OHLC data from Yahoo Finance with retry and caching"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize fetcher

        Args:
            instrument: Trading instrument symbol (e.g., NQ=F)
        """
        self.instrument = instrument
        self.cache: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[datetime] = None

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self.cache is None or self.cache_timestamp is None:
            return False

        age = (datetime.now() - self.cache_timestamp).total_seconds()
        return age < YFINANCE_CACHE_TTL

    def fetch_ohlc(
        self,
        period: str = "1d",
        interval: str = "1m",
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data from Yahoo Finance

        Args:
            period: Time period (e.g., '1d', '5d', '1mo')
            interval: Data interval (e.g., '1m', '5m', '15m', '1h')
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with OHLC data or None if fetch failed
        """
        # Check cache
        if use_cache and self._is_cache_valid():
            logger.debug(f"Using cached data for {self.instrument}")
            return self.cache.get("data")

        # Fetch with retry logic
        for attempt in range(1, YFINANCE_RETRY_ATTEMPTS + 1):
            try:
                logger.info(f"Fetching {self.instrument} data (attempt {attempt}/{YFINANCE_RETRY_ATTEMPTS})")

                ticker = yf.Ticker(self.instrument)
                df = ticker.history(period=period, interval=interval)

                if df.empty:
                    logger.warning(f"No data returned for {self.instrument}")
                    if attempt < YFINANCE_RETRY_ATTEMPTS:
                        time.sleep(YFINANCE_RETRY_DELAY * attempt)
                        continue
                    return None

                # Clean and prepare data
                df = df.reset_index()

                # Rename columns to lowercase
                df.columns = [col.lower() for col in df.columns]

                # Ensure datetime column
                if 'datetime' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['datetime'])
                elif 'date' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['date'])
                else:
                    logger.error("No datetime column found in data")
                    return None

                # Select relevant columns
                required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = df[required_cols]

                # Sort by timestamp
                df = df.sort_values('timestamp').reset_index(drop=True)

                # Update cache
                self.cache = {"data": df, "period": period, "interval": interval}
                self.cache_timestamp = datetime.now()

                logger.info(f"Successfully fetched {len(df)} bars for {self.instrument}")
                return df

            except Exception as e:
                logger.error(f"Error fetching data (attempt {attempt}): {str(e)}")
                if attempt < YFINANCE_RETRY_ATTEMPTS:
                    time.sleep(YFINANCE_RETRY_DELAY * attempt)
                else:
                    logger.error(f"Failed to fetch data after {YFINANCE_RETRY_ATTEMPTS} attempts")
                    return None

        return None

    def get_latest_price(self) -> Optional[float]:
        """
        Get latest close price

        Returns:
            Latest close price or None if unavailable
        """
        df = self.fetch_ohlc(period="1d", interval="1m")
        if df is None or df.empty:
            return None

        return float(df.iloc[-1]['close'])

    def get_current_bar(self) -> Optional[Dict[str, Any]]:
        """
        Get current 1-minute bar

        Returns:
            Dict with OHLCV data or None if unavailable
        """
        df = self.fetch_ohlc(period="1d", interval="1m")
        if df is None or df.empty:
            return None

        latest = df.iloc[-1]
        return {
            'timestamp': latest['timestamp'],
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'close': float(latest['close']),
            'volume': int(latest['volume']),
        }

    def get_session_data(self, session_start: datetime, session_end: datetime) -> Optional[pd.DataFrame]:
        """
        Get OHLC data for a specific session

        Args:
            session_start: Session start datetime
            session_end: Session end datetime

        Returns:
            DataFrame with session OHLC data or None
        """
        # Fetch enough data to cover the session
        df = self.fetch_ohlc(period="5d", interval="1m", use_cache=False)
        if df is None or df.empty:
            return None

        # Filter to session timeframe
        mask = (df['timestamp'] >= session_start) & (df['timestamp'] <= session_end)
        session_df = df.loc[mask].copy()

        if session_df.empty:
            logger.warning(f"No data found for session {session_start} to {session_end}")
            return None

        return session_df

    def get_period_high_low(self, start: datetime, end: datetime) -> Optional[Dict[str, float]]:
        """
        Get high and low for a specific period

        Args:
            start: Period start datetime
            end: Period end datetime

        Returns:
            Dict with 'high' and 'low' or None
        """
        df = self.get_session_data(start, end)
        if df is None or df.empty:
            return None

        return {
            'high': float(df['high'].max()),
            'low': float(df['low'].min()),
        }

    def clear_cache(self):
        """Clear the data cache"""
        self.cache = None
        self.cache_timestamp = None
        logger.debug("Cache cleared")


# Global instance
fetcher = YahooFinanceFetcher()
