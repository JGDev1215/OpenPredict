-- Migration 005: Data Compression Policies
-- Compress data older than 7 days to save 60% storage while maintaining performance

-- ============================================================================
-- COMPRESSION POLICIES
-- ============================================================================

-- OHLC_DATA: Compress chunks older than 7 days (reduce ~60% storage)
SELECT add_compression_policy('ohlc_data',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- SCORE_HISTORY: Compress chunks older than 7 days
SELECT add_compression_policy('score_history',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- LIQUIDITY_EVENTS: Compress chunks older than 7 days
SELECT add_compression_policy('liquidity_events',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- MARKET_STRUCTURE: Compress chunks older than 7 days
SELECT add_compression_policy('market_structure',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- FVG_ZONES: Compress chunks older than 7 days
SELECT add_compression_policy('fvg_zones',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- HOURLY_BLOCKS: Compress chunks older than 7 days
SELECT add_compression_policy('hourly_blocks',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- COMPRESSION STATISTICS & MONITORING
-- ============================================================================

-- View compression status of all chunks
SELECT
    chunk_name,
    table_name,
    compression_status,
    pg_size_pretty(before_compression_total_bytes) as before_compression,
    pg_size_pretty(after_compression_total_bytes) as after_compression,
    ROUND(
        100 - (after_compression_total_bytes::decimal / before_compression_total_bytes * 100),
        2
    ) as compression_ratio_percent
FROM timescaledb_information.compressed_chunk_stats
ORDER BY table_name, chunk_name DESC;

-- Verify compression policies are in place
SELECT
    hypertable_name,
    older_than,
    IF(compress => true, 'enabled', 'disabled') as compression_status
FROM timescaledb_information.compression_settings
WHERE hypertable_name IN (
    'ohlc_data', 'score_history', 'liquidity_events',
    'market_structure', 'fvg_zones', 'hourly_blocks'
)
ORDER BY hypertable_name;

-- ============================================================================
-- MANUAL COMPRESSION (If needed for immediate compression)
-- ============================================================================

-- Compress chunks older than 7 days for ohlc_data
-- SELECT compress_chunk(show_chunks('ohlc_data', INTERVAL '7 days'));

-- Compress all chunks for score_history
-- SELECT compress_chunk(show_chunks('score_history', INTERVAL '7 days'));

-- ============================================================================
-- DECOMPRESSION (If needed to revert compression)
-- ============================================================================

-- Decompress chunks older than 7 days (uncompress after compression)
-- SELECT decompress_chunk(show_chunks('ohlc_data', INTERVAL '7 days'));

-- ============================================================================
-- STORAGE SAVINGS ESTIMATION
-- ============================================================================

-- Expected storage savings with compression (60% reduction):
-- - OHLC_DATA: ~1,440 rows/day × 30 days = ~43,200 rows
--   Uncompressed: ~5-10MB/month
--   Compressed: ~2-4MB/month (saves ~60%)
--
-- - SCORE_HISTORY: ~480 rows/day × 30 days = ~14,400 rows
--   Uncompressed: ~2-4MB/month
--   Compressed: ~0.8-1.6MB/month (saves ~60%)
--
-- Total estimated: ~2.8-5.6MB compressed per month
--
-- Cost calculation (Supabase pricing ~$0.125/GB):
-- - 30 days: ~90MB = $0.01125/month
-- - 365 days: ~1.1GB = $0.14/year

-- ============================================================================
-- PERFORMANCE IMPACT OF COMPRESSION
-- ============================================================================

-- Note: Compressed chunks have slight performance overhead on read queries
-- Typically adds 5-10ms to decompression on access
-- Trade-off: 60% storage savings vs. 5-10ms query latency increase
-- For this system: Worth it! Query response time is still <200ms target

-- To minimize compression impact:
-- 1. Queries on recent data (< 7 days) hit uncompressed chunks (fast)
-- 2. Queries on older data accept slight decompression overhead
-- 3. Background cleanup jobs run during off-hours to minimize impact

-- ============================================================================
-- END OF MIGRATION 005
-- Run migration 006 to enable real-time subscriptions
-- ============================================================================
