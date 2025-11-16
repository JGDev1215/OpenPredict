-- Migration 003: Advanced Indexing Strategy
-- B-tree indexes for filtering, BRIN indexes for range scans, GIN for JSONB

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- OHLC_DATA: Latest price queries (<50ms target)
CREATE INDEX IF NOT EXISTS idx_ohlc_latest_price ON ohlc_data (instrument, timestamp DESC)
    WHERE timestamp > NOW() - INTERVAL '1 hour';

-- SCORE_HISTORY: Latest scores for API endpoint (<50ms target)
CREATE INDEX IF NOT EXISTS idx_score_latest_bullish ON score_history (instrument, bullish_total DESC, calculation_time DESC)
    WHERE calculation_time > NOW() - INTERVAL '24 hours';

CREATE INDEX IF NOT EXISTS idx_score_latest_bearish ON score_history (instrument, bearish_total DESC, calculation_time DESC)
    WHERE calculation_time > NOW() - INTERVAL '24 hours';

-- LIQUIDITY_EVENTS: Time-range queries
CREATE INDEX IF NOT EXISTS idx_liquidity_quality ON liquidity_events (quality_factor DESC, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_liquidity_recent ON liquidity_events (timestamp DESC, instrument)
    WHERE timestamp > NOW() - INTERVAL '24 hours';

-- MARKET_STRUCTURE: Structure break queries
CREATE INDEX IF NOT EXISTS idx_structure_recent ON market_structure (timestamp DESC, structure_type)
    WHERE timestamp > NOW() - INTERVAL '7 days';

-- FVG_ZONES: Find unfilled FVGs
CREATE INDEX IF NOT EXISTS idx_fvg_unfilled ON fvg_zones (timestamp_created DESC)
    WHERE filled = FALSE;

-- HOURLY_BLOCKS: Block number queries
CREATE INDEX IF NOT EXISTS idx_blocks_recent ON hourly_blocks (hour_start DESC, block_number)
    WHERE hour_start > NOW() - INTERVAL '24 hours';

-- REFERENCE_LEVELS: Quick level lookups
CREATE INDEX IF NOT EXISTS idx_ref_levels_latest ON reference_levels (instrument, level_type)
    WHERE timestamp_created > DATE_TRUNC('day', NOW());

-- ============================================================================
-- JSONB INDEXES FOR COMPONENT BREAKDOWN
-- ============================================================================

-- Fast filtering on bullish components
CREATE INDEX IF NOT EXISTS idx_score_bullish_htf_bias ON score_history
    USING GIN ((bullish_components -> 'htf_bias'));

CREATE INDEX IF NOT EXISTS idx_score_bullish_kill_zone ON score_history
    USING GIN ((bullish_components -> 'kill_zone'));

CREATE INDEX IF NOT EXISTS idx_score_bullish_pd_array ON score_history
    USING GIN ((bullish_components -> 'pd_array'));

-- Fast filtering on bearish components
CREATE INDEX IF NOT EXISTS idx_score_bearish_htf_bias ON score_history
    USING GIN ((bearish_components -> 'htf_bias'));

CREATE INDEX IF NOT EXISTS idx_score_bearish_kill_zone ON score_history
    USING GIN ((bearish_components -> 'kill_zone'));

CREATE INDEX IF NOT EXISTS idx_score_bearish_pd_array ON score_history
    USING GIN ((bearish_components -> 'pd_array'));

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- ============================================================================

-- Query: Get all OHLC data for a date range and instrument
CREATE INDEX IF NOT EXISTS idx_ohlc_date_range ON ohlc_data (instrument, timestamp DESC)
    INCLUDE (open, high, low, close, volume);

-- Query: Get scores within a time range with specific rating
CREATE INDEX IF NOT EXISTS idx_score_rating_time ON score_history (instrument, bias_strength, calculation_time DESC);

-- Query: Find prediction accuracy
CREATE INDEX IF NOT EXISTS idx_predictions_accuracy ON block_predictions (instrument, prediction_correct, prediction_time DESC);

-- ============================================================================
-- PARTIAL INDEXES FOR COMMON FILTERS
-- ============================================================================

-- Error logs in past 7 days (retention period)
CREATE INDEX IF NOT EXISTS idx_error_recent ON error_log (timestamp DESC)
    WHERE timestamp > NOW() - INTERVAL '7 days';

-- Elite-rated scores (high-quality setups)
CREATE INDEX IF NOT EXISTS idx_score_elite ON score_history (calculation_time DESC)
    WHERE bias_strength = 'ELITE';

-- High-confidence predictions
CREATE INDEX IF NOT EXISTS idx_predictions_high_confidence ON block_predictions (prediction_time DESC)
    WHERE confidence >= 80;

-- ============================================================================
-- VERIFY INDEX CREATION
-- ============================================================================

-- Query to check all indexes on score_history (most critical table)
SELECT
    indexname,
    indexdef,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'score_history'
ORDER BY idx_scan DESC;

-- ============================================================================
-- INDEX USAGE MONITORING (Optional - for future analysis)
-- ============================================================================

-- Enable pg_stat_statements for index performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================================
-- END OF MIGRATION 003
-- Run migration 004 to apply retention policies
-- ============================================================================
