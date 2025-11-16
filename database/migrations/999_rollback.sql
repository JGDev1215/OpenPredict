-- Migration 999: Full Rollback Script
-- WARNING: This script completely removes all tables and structures created by migrations 001-007
-- Use only if you need to completely reset the database

-- ============================================================================
-- DISABLE CONSTRAINTS AND TRIGGERS (for clean deletion)
-- ============================================================================

-- Disable all triggers
ALTER TABLE score_history DISABLE TRIGGER trigger_score_insert;
ALTER TABLE score_history DISABLE TRIGGER trigger_score_update;

-- ============================================================================
-- DROP MATERIALIZED VIEWS
-- ============================================================================

DROP MATERIALIZED VIEW IF EXISTS mv_agent_performance CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_score_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_hourly_block_accuracy CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_recent_scores_24h CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_latest_fibonacci_pivots CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_latest_reference_levels CASCADE;

-- ============================================================================
-- DROP FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS notify_score_update() CASCADE;
DROP FUNCTION IF EXISTS cleanup_error_logs() CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_reference_levels() CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_fibonacci_pivots() CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_block_predictions() CASCADE;

-- ============================================================================
-- DROP TABLES (TimescaleDB will clean up hypertables automatically)
-- ============================================================================

DROP TABLE IF EXISTS score_history CASCADE;
DROP TABLE IF EXISTS hourly_blocks CASCADE;
DROP TABLE IF EXISTS fvg_zones CASCADE;
DROP TABLE IF EXISTS market_structure CASCADE;
DROP TABLE IF EXISTS liquidity_events CASCADE;
DROP TABLE IF EXISTS fibonacci_pivots CASCADE;
DROP TABLE IF EXISTS reference_levels CASCADE;
DROP TABLE IF EXISTS ohlc_data CASCADE;
DROP TABLE IF EXISTS block_predictions CASCADE;
DROP TABLE IF EXISTS error_log CASCADE;

-- ============================================================================
-- DROP ENUM TYPES
-- ============================================================================

DROP TYPE IF EXISTS trigger_source_enum CASCADE;
DROP TYPE IF EXISTS structure_type_enum CASCADE;
DROP TYPE IF EXISTS event_type_enum CASCADE;
DROP TYPE IF EXISTS rating_enum CASCADE;
DROP TYPE IF EXISTS direction_enum CASCADE;

-- ============================================================================
-- DROP PUBLICATION (for Realtime)
-- ============================================================================

DROP PUBLICATION IF EXISTS supabase_realtime_score_updates CASCADE;

-- ============================================================================
-- DROP CRON JOBS (if pg_cron was installed)
-- ============================================================================

-- These will fail silently if pg_cron is not installed
-- SELECT cron.unschedule('cleanup_error_logs_job');
-- SELECT cron.unschedule('cleanup_reference_levels_job');
-- SELECT cron.unschedule('cleanup_fibonacci_pivots_job');
-- SELECT cron.unschedule('cleanup_block_predictions_job');
-- SELECT cron.unschedule('refresh_mv_ref_levels');
-- SELECT cron.unschedule('refresh_mv_recent_scores');
-- SELECT cron.unschedule('refresh_mv_block_accuracy');
-- SELECT cron.unschedule('refresh_mv_daily_stats');
-- SELECT cron.unschedule('refresh_mv_agent_perf');

-- ============================================================================
-- VERIFY CLEANUP
-- ============================================================================

-- Check that all tables are removed
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check that all hypertables are removed
SELECT
    hypertable_name
FROM timescaledb_information.hypertables
WHERE hypertable_name IN (
    'ohlc_data', 'score_history', 'liquidity_events',
    'market_structure', 'fvg_zones', 'hourly_blocks'
);

-- Check that all materialized views are removed
SELECT
    matviewname
FROM pg_matviews
WHERE matviewname LIKE 'mv_%';

-- ============================================================================
-- OPTIONAL: DISABLE TIMESCALEDB EXTENSION
-- ============================================================================

-- WARNING: Only run if you want to remove TimescaleDB entirely
-- This is not recommended for Supabase unless you're completely resetting

-- DROP EXTENSION IF EXISTS timescaledb CASCADE;

-- ============================================================================
-- END OF ROLLBACK SCRIPT
-- ============================================================================

-- After running this script, you can re-run migrations 001-007 to rebuild the database
