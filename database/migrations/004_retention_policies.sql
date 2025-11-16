-- Migration 004: Data Retention Policies
-- Auto-cleanup for old data to maintain database performance and cost efficiency

-- ============================================================================
-- RETENTION POLICY: 30 DAYS
-- ============================================================================

-- OHLC_DATA: Keep 30 days of 1-minute bars (~43,200 rows)
SELECT add_retention_policy('ohlc_data',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- SCORE_HISTORY: Keep 30 days of score history (~14,400 rows)
SELECT add_retention_policy('score_history',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- LIQUIDITY_EVENTS: Keep 30 days (~1,500-3,000 events)
SELECT add_retention_policy('liquidity_events',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- MARKET_STRUCTURE: Keep 30 days (~900-1,500 breaks)
SELECT add_retention_policy('market_structure',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- FVG_ZONES: Keep 30 days (~600-1,200 FVGs)
SELECT add_retention_policy('fvg_zones',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- HOURLY_BLOCKS: Keep 30 days (~5,040 blocks)
SELECT add_retention_policy('hourly_blocks',
    INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- RETENTION POLICY: 7 DAYS (Error logs)
-- ============================================================================

-- ERROR_LOG: Keep 7 days of errors for debugging
-- Note: Error log is not a hypertable, so we use standard PostgreSQL deletion
CREATE OR REPLACE FUNCTION cleanup_error_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM error_log
    WHERE timestamp < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RETENTION POLICY: 30 DAYS (Reference levels - manual cleanup)
-- ============================================================================

-- REFERENCE_LEVELS: Keep current + 1 day backup
CREATE OR REPLACE FUNCTION cleanup_old_reference_levels()
RETURNS void AS $$
BEGIN
    DELETE FROM reference_levels
    WHERE timestamp_created < DATE_TRUNC('day', NOW()) - INTERVAL '1 day'
    AND level_type IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RETENTION POLICY: 30 DAYS (Fibonacci pivots - manual cleanup)
-- ============================================================================

-- FIBONACCI_PIVOTS: Keep current + 1 day backup
CREATE OR REPLACE FUNCTION cleanup_old_fibonacci_pivots()
RETURNS void AS $$
BEGIN
    DELETE FROM fibonacci_pivots
    WHERE valid_from < DATE_TRUNC('day', NOW()) - INTERVAL '1 day'
    AND timeframe IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RETENTION POLICY: 90 DAYS (Block predictions - for accuracy analysis)
-- ============================================================================

-- BLOCK_PREDICTIONS: Keep 90 days for long-term accuracy tracking
CREATE OR REPLACE FUNCTION cleanup_old_block_predictions()
RETURNS void AS $$
BEGIN
    DELETE FROM block_predictions
    WHERE prediction_time < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTOMATED CLEANUP JOBS (Cron-based)
-- ============================================================================

-- Install pg_cron extension for scheduling
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Job 1: Cleanup error logs every day at 3:00 AM UTC
SELECT cron.schedule(
    'cleanup_error_logs_job',
    '0 3 * * *',  -- Daily at 3:00 AM UTC
    'SELECT cleanup_error_logs()'
);

-- Job 2: Cleanup reference levels every day at 3:15 AM UTC
SELECT cron.schedule(
    'cleanup_reference_levels_job',
    '15 3 * * *',  -- Daily at 3:15 AM UTC
    'SELECT cleanup_old_reference_levels()'
);

-- Job 3: Cleanup Fibonacci pivots every day at 3:30 AM UTC
SELECT cron.schedule(
    'cleanup_fibonacci_pivots_job',
    '30 3 * * *',  -- Daily at 3:30 AM UTC
    'SELECT cleanup_old_fibonacci_pivots()'
);

-- Job 4: Cleanup old block predictions every week at 4:00 AM UTC
SELECT cron.schedule(
    'cleanup_block_predictions_job',
    '0 4 * * 0',  -- Weekly on Sunday at 4:00 AM UTC
    'SELECT cleanup_old_block_predictions()'
);

-- ============================================================================
-- MONITOR RETENTION POLICY STATUS
-- ============================================================================

-- Check all active retention policies
SELECT
    hypertable_name,
    older_than,
    IF(cascade_children => true, 'yes', 'no') as cascade
FROM timescaledb_information.retention_policies
ORDER BY hypertable_name;

-- Check retention policy execution history
-- Note: This view shows when retention policies are scheduled to run
SELECT
    job_id,
    hypertable_name,
    policy_type,
    config
FROM timescaledb_information.jobs
WHERE hypertable_name IN (
    'ohlc_data', 'score_history', 'liquidity_events',
    'market_structure', 'fvg_zones', 'hourly_blocks'
)
ORDER BY hypertable_name;

-- ============================================================================
-- MANUAL RETENTION CLEANUP (For immediate cleanup if needed)
-- ============================================================================

-- EMERGENCY: Immediately drop chunks older than 30 days
-- USE WITH CAUTION - This is destructive
-- SELECT drop_chunks('ohlc_data', INTERVAL '30 days');
-- SELECT drop_chunks('score_history', INTERVAL '30 days');

-- ============================================================================
-- STORAGE MONITORING
-- ============================================================================

-- Check total database size
SELECT
    pg_size_pretty(pg_database_size('postgres')) as database_size;

-- Check size of each hypertable
SELECT
    hypertable_name,
    pg_size_pretty(total_bytes) as table_size,
    pg_size_pretty(index_bytes) as index_size
FROM timescaledb_information.hypertable_detailed_size
WHERE hypertable_name IN (
    'ohlc_data', 'score_history', 'liquidity_events',
    'market_structure', 'fvg_zones', 'hourly_blocks'
)
ORDER BY total_bytes DESC;

-- Estimate monthly storage with compression
-- Assuming ~43,200 OHLC rows + ~14,400 score rows per day
-- With 60% compression: ~2.7GB per month → ~90MB/day

-- ============================================================================
-- END OF MIGRATION 004
-- Run migration 005 to apply compression policies
-- ============================================================================
