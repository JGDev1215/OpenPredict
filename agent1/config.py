"""
Configuration module for Agent 1 - Data Collector
Loads environment variables and provides configuration constants
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Trading Configuration
INSTRUMENT = os.getenv("INSTRUMENT", "NQ=F")
FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", "60"))

# Timezone Configuration
MARKET_TIMEZONE = os.getenv("MARKET_TIMEZONE", "America/New_York")
UTC_TIMEZONE = os.getenv("UTC_TIMEZONE", "UTC")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "agent1.log")

# yfinance Configuration
YFINANCE_RETRY_ATTEMPTS = 3
YFINANCE_RETRY_DELAY = 2  # seconds
YFINANCE_CACHE_TTL = 50  # seconds

# Market Configuration
PIPS_PER_POINT = 0.25  # For NQ futures
MIN_FVG_SIZE = 2  # minimum gap size in points
BLOCKS_PER_HOUR = 7
BLOCK_DURATION_MINUTES = 60 / BLOCKS_PER_HOUR  # ~8.57 minutes

# Trading Sessions (in ET)
SESSIONS = {
    "ASIAN": {"start": "18:00", "end": "02:00"},
    "LONDON": {"start": "03:00", "end": "12:00"},
    "NY_AM": {"start": "08:30", "end": "12:00"},
    "NY_PM": {"start": "13:00", "end": "17:00"},
}

# Market Hours (NYSE hours in ET)
MARKET_OPEN_HOUR = 9  # 9:30 AM ET
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16  # 4:00 PM ET
MARKET_CLOSE_MINUTE = 0

# Displacement Thresholds (for market structure)
STRONG_DISPLACEMENT_PIPS = 20
STRONG_DISPLACEMENT_MINUTES = 15

# Liquidity Event Quality Scores
LIQUIDITY_QUALITY = {
    "CLEAN_SWEEP": 1.0,
    "WICK": 0.8,
    "NEAR_MISS": 0.4,
}

# Liquidity Hold Time Bonuses
HOLD_BONUSES = {
    "LONG": 0.20,    # > 2 hours
    "MEDIUM": 0.10,  # 1-2 hours
    "SHORT": 0.05,   # 30min-1hr
}

# Liquidity Event Weights
LIQUIDITY_WEIGHTS = {
    "ASIA_RANGE": 3.0,
    "PREV_DAY_HL": 2.5,
    "EQUAL_HL": 2.0,
    "SESSION_HL": 1.5,
}

# Structure Break Types
STRUCTURE_BREAK_TYPES = {
    "MAJOR": 3.0,
    "INTERMEDIATE": 2.0,
    "MINOR": 1.0,
}
