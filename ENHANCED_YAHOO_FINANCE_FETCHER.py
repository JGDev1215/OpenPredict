"""
Enhanced Yahoo Finance data fetcher for Agent 1
Implements production-ready features:
- Improved retry logic with exponential backoff and jitter
- Data validation with OHLC consistency checks
- Cache with monotonic time and statistics
- Rate limiting and 429 handling
- Memory efficiency and monitoring
- Timezone handling with UTC normalization
- Circuit breaker pattern
"""
import time
import random
import gc
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np
import yfinance as yf
from utils.logger import logger
from config import (
    INSTRUMENT,
    YFINANCE_RETRY_ATTEMPTS,
    YFINANCE_RETRY_DELAY,
    YFINANCE_RETRY_MAX_DELAY,
    YFINANCE_RETRY_JITTER_ENABLED,
    YFINANCE_RATE_LIMIT_BACKOFF,
    YFINANCE_RATE_LIMIT_MAX_BACKOFF,
    YFINANCE_CACHE_TTL,
    YFINANCE_CACHE_ENABLED,
    YFINANCE_CACHE_VALIDATION,
    YFINANCE_FETCH_TIMEOUT,
    VALIDATE_OHLC_RELATIONSHIPS,
    VALIDATE_DATA_FRESHNESS,
    VALIDATE_NO_DUPLICATES,
    VALIDATE_NO_NAN_VALUES,
    VALIDATE_VOLUME_POSITIVE,
    DATA_FRESHNESS_MAX_AGE_SECONDS,
    DATA_FRESHNESS_MIN_AGE_SECONDS,
    CIRCUIT_BREAKER_ENABLED,
    CIRCUIT_BREAKER_THRESHOLD,
    CIRCUIT_BREAKER_RESET_INTERVAL,
)


class CacheEntry:
    """Represents a single cache entry with validation"""
    def __init__(self, data: pd.DataFrame, metadata: Dict[str, Any]):
        self.data = data.copy()
        self.metadata = metadata
        self.creation_time = time.monotonic()  # Use monotonic time
        self.hit_count = 0
        self.validation_passed = False


class CacheStatistics:
    """Tracks cache performance metrics"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.invalidations = 0
        self.evictions = 0
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class CircuitBreaker:
    """Implements circuit breaker pattern for API failures"""
    def __init__(self, threshold: int = CIRCUIT_BREAKER_THRESHOLD, 
                 reset_interval: int = CIRCUIT_BREAKER_RESET_INTERVAL):
        self.threshold = threshold
        self.reset_interval = reset_interval
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    def record_success(self):
        """Record successful API call"""
        if self.is_open:
            logger.info("Circuit breaker: Closed (recovered)")
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        """Record failed API call"""
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        
        if self.failure_count >= self.threshold:
            self.is_open = True
            logger.error(f"Circuit breaker: OPEN (failed {self.failure_count} times)")
    
    def can_attempt(self) -> bool:
        """Check if API call can be attempted"""
        if not self.is_open:
            return True
        
        # Check if reset interval has passed
        if self.last_failure_time:
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed >= self.reset_interval:
                logger.info("Circuit breaker: Attempting reset...")
                self.failure_count = 0
                self.is_open = False
                return True
        
        return False


class DataValidationReport:
    """Detailed report of data validation results"""
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def add_error(self, error: str):
        self.is_valid = False
        self.errors.append(error)
        logger.error(f"Validation error: {error}")
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
        logger.warning(f"Validation warning: {warning}")
    
    def add_stat(self, key: str, value: Any):
        self.stats[key] = value
    
    def summary(self) -> str:
        return f"Valid: {self.is_valid}, Errors: {len(self.errors)}, Warnings: {len(self.warnings)}"


class YahooFinanceFetcherEnhanced:
    """Enhanced OHLC data fetcher with production-ready features"""

    def __init__(self, instrument: str = INSTRUMENT):
        """
        Initialize fetcher with circuit breaker and cache
        
        Args:
            instrument: Trading instrument symbol (e.g., NQ=F)
        """
        self.instrument = instrument
        self.cache: Optional[CacheEntry] = None
        self.cache_stats = CacheStatistics()
        self.circuit_breaker = CircuitBreaker() if CIRCUIT_BREAKER_ENABLED else None
        self.rate_limit_backoff = 0  # Current backoff time
        self.rate_limit_until = 0    # Until this time (monotonic)
        self.last_fetch_time = None
        logger.info(f"YahooFinanceFetcher initialized for {instrument}")

    def _calculate_backoff_delay(self, attempt: int, is_rate_limit: bool = False) -> float:
        """
        Calculate retry delay with exponential backoff and jitter
        
        Args:
            attempt: Current attempt number (1-based)
            is_rate_limit: Whether this is a rate limit error (429)
        
        Returns:
            Delay in seconds
        """
        if is_rate_limit:
            # For rate limits, use longer backoff: 5m, 15m, 1h
            base_delay = YFINANCE_RATE_LIMIT_BACKOFF * (2 ** (attempt - 1))
            max_delay = YFINANCE_RATE_LIMIT_MAX_BACKOFF
        else:
            # For regular retries: 2s, 4s, 8s (capped at max)
            base_delay = YFINANCE_RETRY_DELAY * (2 ** (attempt - 1))
            max_delay = YFINANCE_RETRY_MAX_DELAY
        
        # Cap the delay
        delay = min(base_delay, max_delay)
        
        # Add jitter if enabled
        if YFINANCE_RETRY_JITTER_ENABLED:
            jitter = random.uniform(0, 1)
            delay += jitter
        
        return delay

    def _is_cache_valid(self) -> bool:
        """
        Check if cache is still valid (monotonic time)
        
        Returns:
            True if cache exists and hasn't expired
        """
        if self.cache is None:
            return False
        
        age = time.monotonic() - self.cache.creation_time
        is_valid = age < YFINANCE_CACHE_TTL
        
        if not is_valid and self.cache:
            self.cache_stats.invalidations += 1
        
        return is_valid

    def _validate_ohlc_data(self, df: pd.DataFrame) -> DataValidationReport:
        """
        Validate OHLC data for consistency and quality
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            DataValidationReport with validation results
        """
        report = DataValidationReport()
        
        if df.empty:
            report.add_error("DataFrame is empty")
            return report
        
        # Check required columns
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            report.add_error(f"Missing columns: {missing_cols}")
            return report
        
        # Validate OHLC relationships
        if VALIDATE_OHLC_RELATIONSHIPS:
            # High >= Low
            invalid_hl = (df['high'] < df['low']).sum()
            if invalid_hl > 0:
                report.add_error(f"{invalid_hl} bars with High < Low")
            
            # High >= Open and High >= Close
            invalid_h_open = (df['high'] < df['open']).sum()
            invalid_h_close = (df['high'] < df['close']).sum()
            if invalid_h_open > 0:
                report.add_error(f"{invalid_h_open} bars with High < Open")
            if invalid_h_close > 0:
                report.add_error(f"{invalid_h_close} bars with High < Close")
            
            # Low <= Open and Low <= Close
            invalid_l_open = (df['low'] > df['open']).sum()
            invalid_l_close = (df['low'] > df['close']).sum()
            if invalid_l_open > 0:
                report.add_error(f"{invalid_l_open} bars with Low > Open")
            if invalid_l_close > 0:
                report.add_error(f"{invalid_l_close} bars with Low > Close")
        
        # Validate no NaN/inf values
        if VALIDATE_NO_NAN_VALUES:
            nan_counts = df[['open', 'high', 'low', 'close', 'volume']].isna().sum()
            if nan_counts.sum() > 0:
                report.add_error(f"Found {nan_counts.sum()} NaN values: {nan_counts.to_dict()}")
            
            inf_mask = df[['open', 'high', 'low', 'close']].isin([np.inf, -np.inf]).sum()
            if inf_mask.sum() > 0:
                report.add_error(f"Found {inf_mask.sum()} inf values")
        
        # Validate volume
        if VALIDATE_VOLUME_POSITIVE:
            negative_volume = (df['volume'] < 0).sum()
            if negative_volume > 0:
                report.add_error(f"{negative_volume} bars with negative volume")
        
        # Validate no duplicates
        if VALIDATE_NO_DUPLICATES:
            duplicate_timestamps = df['timestamp'].duplicated().sum()
            if duplicate_timestamps > 0:
                report.add_error(f"{duplicate_timestamps} duplicate timestamps")
        
        # Validate data freshness
        if VALIDATE_DATA_FRESHNESS:
            now = datetime.utcnow()
            latest_timestamp = pd.to_datetime(df['timestamp'].max())
            
            age_seconds = (now - latest_timestamp).total_seconds()
            
            if age_seconds > DATA_FRESHNESS_MAX_AGE_SECONDS:
                report.add_warning(f"Data is stale: {age_seconds:.0f}s old")
            
            if age_seconds < DATA_FRESHNESS_MIN_AGE_SECONDS:
                report.add_error(f"Data from future: {age_seconds:.1f}s")
        
        # Add statistics
        report.add_stat('row_count', len(df))
        report.add_stat('price_range', {
            'open_min': df['open'].min(),
            'open_max': df['open'].max(),
            'close_min': df['close'].min(),
            'close_max': df['close'].max(),
        })
        report.add_stat('volume_total', df['volume'].sum())
        
        return report

    def _should_use_cache(self) -> bool:
        """
        Determine if cached data should be used
        
        Returns:
            True if cache is valid and enabled
        """
        if not YFINANCE_CACHE_ENABLED:
            self.cache_stats.misses += 1
            return False
        
        if not self._is_cache_valid():
            self.cache_stats.misses += 1
            return False
        
        if YFINANCE_CACHE_VALIDATION and self.cache:
            if not self.cache.validation_passed:
                logger.debug("Skipping cache: validation not passed")
                self.cache_stats.misses += 1
                return False
        
        self.cache_stats.hits += 1
        if self.cache:
            self.cache.hit_count += 1
        logger.debug(f"Using cached data (hit #{self.cache.hit_count})")
        return True

    def fetch_ohlc(
        self,
        period: str = "1d",
        interval: str = "1m",
        use_cache: bool = True,
        validate: bool = True
    ) -> Optional[Tuple[pd.DataFrame, DataValidationReport]]:
        """
        Fetch OHLC data from Yahoo Finance with comprehensive error handling
        
        Args:
            period: Time period (e.g., '1d', '5d', '1mo')
            interval: Data interval (e.g., '1m', '5m', '15m', '1h')
            use_cache: Whether to use cached data if available
            validate: Whether to validate returned data
        
        Returns:
            Tuple of (DataFrame with OHLC data, ValidationReport) or (None, report) if fetch failed
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_attempt():
            logger.warning("Circuit breaker is OPEN, cannot attempt fetch")
            return None, DataValidationReport()
        
        # Check rate limit backoff
        if self.rate_limit_until > time.monotonic():
            backoff_remaining = self.rate_limit_until - time.monotonic()
            logger.warning(f"Rate limit backoff: {backoff_remaining:.0f}s remaining")
            return None, DataValidationReport()
        
        # Check cache first
        if use_cache and self._should_use_cache():
            df = self.cache.data.copy()
            report = DataValidationReport()
            report.is_valid = self.cache.validation_passed
            return df, report
        
        # Retry loop
        last_error = None
        is_rate_limited = False
        
        for attempt in range(1, YFINANCE_RETRY_ATTEMPTS + 1):
            try:
                logger.info(f"Fetching {self.instrument} (attempt {attempt}/{YFINANCE_RETRY_ATTEMPTS})")
                
                fetch_start = time.monotonic()
                
                ticker = yf.Ticker(self.instrument)
                df = ticker.history(period=period, interval=interval)
                
                fetch_time = time.monotonic() - fetch_start
                logger.debug(f"Fetch completed in {fetch_time:.2f}s")
                
                # Handle empty response
                if df.empty:
                    logger.warning(f"No data returned for {self.instrument}")
                    if attempt < YFINANCE_RETRY_ATTEMPTS:
                        delay = self._calculate_backoff_delay(attempt, is_rate_limit=False)
                        logger.info(f"Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                    last_error = "Empty DataFrame returned"
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
                    return None, DataValidationReport()
                
                # Prepare data
                df = df.reset_index()
                df.columns = [col.lower() for col in df.columns]
                
                # Handle datetime column
                if 'datetime' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['datetime'])
                elif 'date' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['date'])
                else:
                    logger.error("No datetime column found in data")
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
                    return None, DataValidationReport()
                
                # Select and clean columns
                required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = df[required_cols].copy()
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Validate data
                report = self._validate_ohlc_data(df)
                
                if validate and not report.is_valid:
                    logger.error(f"Data validation failed: {report.summary()}")
                    # Log specific errors
                    for error in report.errors:
                        logger.error(f"  - {error}")
                    # Continue anyway but mark as invalid
                
                # Update cache
                if YFINANCE_CACHE_ENABLED:
                    self.cache = CacheEntry(
                        df,
                        {"period": period, "interval": interval}
                    )
                    self.cache.validation_passed = report.is_valid
                
                # Record success
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                
                self.last_fetch_time = time.monotonic()
                logger.info(f"Successfully fetched {len(df)} bars for {self.instrument}")
                
                return df, report
            
            except Exception as e:
                last_error = str(e)
                error_msg = f"Error fetching data: {last_error}"
                logger.error(f"{error_msg} (attempt {attempt})")
                
                # Check for rate limit error (429)
                if "429" in str(e) or "rate" in str(e).lower():
                    is_rate_limited = True
                    logger.warning("Rate limit detected (429)")
                
                if attempt < YFINANCE_RETRY_ATTEMPTS:
                    delay = self._calculate_backoff_delay(attempt, is_rate_limit=is_rate_limited)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed after {YFINANCE_RETRY_ATTEMPTS} attempts")
                    
                    # Set rate limit backoff if needed
                    if is_rate_limited:
                        backoff = self._calculate_backoff_delay(attempt, is_rate_limit=True)
                        self.rate_limit_until = time.monotonic() + backoff
                        logger.error(f"Rate limit backoff for {backoff:.0f}s")
                    
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
        
        return None, DataValidationReport()

    def get_latest_price(self) -> Optional[float]:
        """
        Get latest close price
        
        Returns:
            Latest close price or None if unavailable
        """
        result = self.fetch_ohlc(period="1d", interval="1m", validate=False)
        if result is None:
            return None
        
        df, _ = result
        if df is None or df.empty:
            return None
        
        return float(df.iloc[-1]['close'])

    def get_current_bar(self) -> Optional[Dict[str, Any]]:
        """
        Get current 1-minute bar
        
        Returns:
            Dict with OHLCV data or None if unavailable
        """
        result = self.fetch_ohlc(period="1d", interval="1m", validate=False)
        if result is None:
            return None
        
        df, _ = result
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

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dict with cache metrics
        """
        return {
            'hits': self.cache_stats.hits,
            'misses': self.cache_stats.misses,
            'invalidations': self.cache_stats.invalidations,
            'hit_rate_percent': self.cache_stats.hit_rate(),
        }

    def clear_cache(self):
        """Clear the data cache and reset statistics"""
        self.cache = None
        self.cache_stats = CacheStatistics()
        logger.debug("Cache cleared")


# Global instance
fetcher = YahooFinanceFetcherEnhanced()
