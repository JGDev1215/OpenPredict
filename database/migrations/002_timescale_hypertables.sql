-- Migration 002: TimescaleDB Hypertables Configuration
-- Converts time-series tables to hypertables for optimal performance

-- ============================================================================
-- CONVERT TABLES TO HYPERTABLES
-- ============================================================================

-- HYPERTABLE 1: ohlc_data (1-day chunks, high frequency)
-- Expected: ~1,440 rows/day
SELECT create_hypertable('ohlc_data', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- HYPERTABLE 2: score_history (7-day chunks, CRITICAL for real-time)
-- Expected: ~480 rows/day
SELECT create_hypertable('score_history', 'calculation_time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- HYPERTABLE 3: liquidity_events (7-day chunks)
-- Expected: ~50-100 events/day
SELECT create_hypertable('liquidity_events', 'timestamp',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- HYPERTABLE 4: market_structure (7-day chunks)
-- Expected: ~30-50 breaks/day
SELECT create_hypertable('market_structure', 'timestamp',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- HYPERTABLE 5: fvg_zones (7-day chunks)
-- Expected: ~20-40 FVGs/day
SELECT create_hypertable('fvg_zones', 'timestamp_created',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- HYPERTABLE 6: hourly_blocks (7-day chunks)
-- Expected: 168 blocks/day
SELECT create_hypertable('hourly_blocks', 'hour_start',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- CONFIGURE HYPERTABLE OPTIONS
-- ============================================================================

-- ohlc_data: Segment by instrument for better compression
ALTER TABLE ohlc_data SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- score_history: Segment by instrument (critical for real-time subscriptions)
ALTER TABLE score_history SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'calculation_time DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- liquidity_events: Segment by instrument
ALTER TABLE liquidity_events SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- market_structure: Segment by instrument
ALTER TABLE market_structure SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- fvg_zones: Segment by instrument
ALTER TABLE fvg_zones SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp_created DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- hourly_blocks: Segment by instrument
ALTER TABLE hourly_blocks SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'hour_start DESC',
    timescaledb.compress_segmentby = 'instrument'
);

-- ============================================================================
-- ENABLE CONSTRAINT EXCLUSION FOR PERFORMANCE
-- ============================================================================

ALTER TABLE ohlc_data SET (timescaledb.skip_scan = off);
ALTER TABLE score_history SET (timescaledb.skip_scan = off);
ALTER TABLE liquidity_events SET (timescaledb.skip_scan = off);

-- ============================================================================
-- REORDER CHUNK DATA FOR BETTER COMPRESSION
-- ============================================================================

-- Reorder ohlc_data chunks for compression
SELECT reorder_chunk(show_chunks('ohlc_data'),
    'idx_ohlc_timestamp_instrument', verbose => TRUE);

-- Reorder score_history chunks for compression
SELECT reorder_chunk(show_chunks('score_history'),
    'idx_score_timestamp_instrument', verbose => TRUE);

-- ============================================================================
-- VERIFY HYPERTABLES CREATED
-- ============================================================================

-- Query to verify hypertable creation
SELECT
    hypertable_name,
    compressed,
    num_chunks,
    pg_size_pretty(total_bytes) as total_size
FROM timescaledb_information.hypertables
WHERE hypertable_name IN (
    'ohlc_data', 'score_history', 'liquidity_events',
    'market_structure', 'fvg_zones', 'hourly_blocks'
)
ORDER BY hypertable_name;

-- ============================================================================
-- END OF MIGRATION 002
-- Run migration 003 to add additional indexes for query optimization
-- ============================================================================
