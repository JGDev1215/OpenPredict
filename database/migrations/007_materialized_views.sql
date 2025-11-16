-- Migration 007: Materialized Views for Common Aggregations
-- Pre-computed views for fast queries on summarized data

-- ============================================================================
-- MATERIALIZED VIEW 1: Latest Reference Levels
-- Refreshed: Every 1 hour or on-demand
-- Purpose: Quick reference for current price context
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_reference_levels AS
SELECT DISTINCT ON (instrument, level_type)
    instrument,
    level_type,
    value,
    timestamp_created
FROM reference_levels
WHERE timestamp_created > NOW() - INTERVAL '7 days'
ORDER BY instrument, level_type, timestamp_created DESC;

CREATE INDEX IF NOT EXISTS idx_mv_ref_levels_instrument ON mv_latest_reference_levels (instrument);
CREATE INDEX IF NOT EXISTS idx_mv_ref_levels_type ON mv_latest_reference_levels (level_type);

COMMENT ON MATERIALIZED VIEW mv_latest_reference_levels IS
    'Latest reference levels for quick lookup (~8 records per instrument)';

-- ============================================================================
-- MATERIALIZED VIEW 2: Latest Fibonacci Pivots
-- Refreshed: Every 1 hour or on-demand
-- Purpose: Quick pivot level access for scoring
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_fibonacci_pivots AS
SELECT DISTINCT ON (instrument, timeframe)
    instrument,
    timeframe,
    pp, r1, r2, r3, s1, s2, s3,
    valid_from
FROM fibonacci_pivots
WHERE valid_from > NOW() - INTERVAL '7 days'
ORDER BY instrument, timeframe, valid_from DESC;

CREATE INDEX IF NOT EXISTS idx_mv_fib_pivots_instrument ON mv_latest_fibonacci_pivots (instrument);
CREATE INDEX IF NOT EXISTS idx_mv_fib_pivots_timeframe ON mv_latest_fibonacci_pivots (timeframe);

COMMENT ON MATERIALIZED VIEW mv_latest_fibonacci_pivots IS
    'Latest Fibonacci pivots for quick lookup (~2 records per instrument)';

-- ============================================================================
-- MATERIALIZED VIEW 3: Recent Scores Summary (Last 24 Hours)
-- Refreshed: Every 5 minutes
-- Purpose: Dashboard display of recent scores with quick filtering
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_recent_scores_24h AS
SELECT
    id,
    calculation_time,
    instrument,
    bullish_total,
    bearish_total,
    directional_bias,
    bias_strength,
    star_rating,
    predicted_block,
    block_confidence,
    trigger_source,
    execution_time_ms,
    data_completeness_percent,
    -- Extract key components for dashboard display
    (bullish_components->>'htf_bias')::numeric as bullish_htf_bias,
    (bullish_components->>'kill_zone')::numeric as bullish_kill_zone,
    (bullish_components->>'pd_array')::numeric as bullish_pd_array,
    (bearish_components->>'htf_bias')::numeric as bearish_htf_bias,
    (bearish_components->>'kill_zone')::numeric as bearish_kill_zone,
    (bearish_components->>'pd_array')::numeric as bearish_pd_array
FROM score_history
WHERE calculation_time > NOW() - INTERVAL '24 hours'
ORDER BY calculation_time DESC;

CREATE INDEX IF NOT EXISTS idx_mv_recent_scores_instrument ON mv_recent_scores_24h (instrument);
CREATE INDEX IF NOT EXISTS idx_mv_recent_scores_bias ON mv_recent_scores_24h (directional_bias);
CREATE INDEX IF NOT EXISTS idx_mv_recent_scores_strength ON mv_recent_scores_24h (bias_strength);

COMMENT ON MATERIALIZED VIEW mv_recent_scores_24h IS
    'Recent scores (24h) with extracted components for dashboard. Refreshed every 5 minutes. (~480 records)';

-- ============================================================================
-- MATERIALIZED VIEW 4: Hourly Block Accuracy Metrics
-- Refreshed: Every 1 hour
-- Purpose: Track prediction accuracy for validation
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_block_accuracy AS
SELECT
    block_number,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN prediction_correct = TRUE THEN 1 ELSE 0 END) as correct_predictions,
    SUM(CASE WHEN prediction_correct = FALSE THEN 1 ELSE 0 END) as incorrect_predictions,
    ROUND(
        AVG(CASE WHEN prediction_correct IS NOT NULL THEN
            CASE WHEN prediction_correct THEN 1.0 ELSE 0.0 END
        END) * 100, 2
    ) as accuracy_percent,
    AVG(confidence) as avg_confidence,
    MIN(prediction_time) as first_prediction_date,
    MAX(prediction_time) as latest_prediction_date
FROM block_predictions
WHERE prediction_time > NOW() - INTERVAL '30 days'
GROUP BY block_number
ORDER BY block_number;

CREATE INDEX IF NOT EXISTS idx_mv_block_accuracy_block_number ON mv_hourly_block_accuracy (block_number);

COMMENT ON MATERIALIZED VIEW mv_hourly_block_accuracy IS
    'Block prediction accuracy metrics for validation. Refreshed hourly. (7 records - one per block)';

-- ============================================================================
-- MATERIALIZED VIEW 5: Daily Score Statistics
-- Refreshed: Every 24 hours (at midnight UTC)
-- Purpose: Summary statistics for performance analysis
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_score_stats AS
SELECT
    DATE(calculation_time) as score_date,
    instrument,
    COUNT(*) as total_scores,
    ROUND(AVG(bullish_total), 2) as avg_bullish_score,
    ROUND(AVG(bearish_total), 2) as avg_bearish_score,
    ROUND(STDDEV(bullish_total), 2) as stddev_bullish,
    ROUND(STDDEV(bearish_total), 2) as stddev_bearish,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms,
    COUNT(CASE WHEN bias_strength = 'ELITE' THEN 1 END) as elite_count,
    COUNT(CASE WHEN bias_strength = 'HIGH' THEN 1 END) as high_count,
    COUNT(CASE WHEN bias_strength = 'ACCEPTABLE' THEN 1 END) as acceptable_count,
    COUNT(CASE WHEN bias_strength = 'MARGINAL' THEN 1 END) as marginal_count,
    COUNT(CASE WHEN bias_strength = 'POOR' THEN 1 END) as poor_count,
    COUNT(CASE WHEN directional_bias = 'BULLISH' THEN 1 END) as bullish_count,
    COUNT(CASE WHEN directional_bias = 'BEARISH' THEN 1 END) as bearish_count,
    COUNT(CASE WHEN directional_bias = 'NEUTRAL' THEN 1 END) as neutral_count
FROM score_history
WHERE calculation_time > NOW() - INTERVAL '30 days'
GROUP BY DATE(calculation_time), instrument
ORDER BY score_date DESC, instrument;

CREATE INDEX IF NOT EXISTS idx_mv_daily_stats_date ON mv_daily_score_stats (score_date DESC);
CREATE INDEX IF NOT EXISTS idx_mv_daily_stats_instrument ON mv_daily_score_stats (instrument);

COMMENT ON MATERIALIZED VIEW mv_daily_score_stats IS
    'Daily score statistics for performance analysis. Refreshed daily. (~30 records)';

-- ============================================================================
-- MATERIALIZED VIEW 6: Agent Performance Monitoring
-- Refreshed: Every 15 minutes
-- Purpose: Monitor Agent 1 and Agent 2 execution health
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_agent_performance AS
SELECT
    agent_name,
    DATE(timestamp) as error_date,
    COUNT(*) as error_count,
    COUNT(DISTINCT error_type) as error_types,
    STRING_AGG(DISTINCT error_type, ', ') as error_type_list,
    MAX(timestamp) as latest_error_time
FROM error_log
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY agent_name, DATE(timestamp)
ORDER BY agent_name, error_date DESC;

CREATE INDEX IF NOT EXISTS idx_mv_agent_perf_agent ON mv_agent_performance (agent_name);
CREATE INDEX IF NOT EXISTS idx_mv_agent_perf_date ON mv_agent_performance (error_date DESC);

COMMENT ON MATERIALIZED VIEW mv_agent_performance IS
    'Agent error tracking for system health monitoring. Refreshed every 15 minutes. (~3-7 records)';

-- ============================================================================
-- REFRESH STRATEGIES
-- ============================================================================

-- Option 1: Manual refresh (on-demand)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_reference_levels;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_recent_scores_24h;

-- Option 2: Scheduled refresh using pg_cron (if available)
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Refresh reference levels every 1 hour
-- SELECT cron.schedule('refresh_mv_ref_levels', '0 * * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_reference_levels'
-- );

-- Refresh recent scores every 5 minutes
-- SELECT cron.schedule('refresh_mv_recent_scores', '*/5 * * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_recent_scores_24h'
-- );

-- Refresh block accuracy every 1 hour
-- SELECT cron.schedule('refresh_mv_block_accuracy', '0 * * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_block_accuracy'
-- );

-- Refresh daily stats every 24 hours at 1:00 AM UTC
-- SELECT cron.schedule('refresh_mv_daily_stats', '0 1 * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_score_stats'
-- );

-- Refresh agent performance every 15 minutes
-- SELECT cron.schedule('refresh_mv_agent_perf', '*/15 * * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_agent_performance'
-- );

-- ============================================================================
-- VERIFY MATERIALIZED VIEWS
-- ============================================================================

-- List all materialized views
SELECT
    schemaname,
    matviewname,
    matviewowner
FROM pg_matviews
WHERE matviewname LIKE 'mv_%'
ORDER BY matviewname;

-- Get row counts for each view
SELECT
    'mv_latest_reference_levels' as view_name,
    COUNT(*) as row_count
FROM mv_latest_reference_levels
UNION ALL
SELECT 'mv_latest_fibonacci_pivots', COUNT(*) FROM mv_latest_fibonacci_pivots
UNION ALL
SELECT 'mv_recent_scores_24h', COUNT(*) FROM mv_recent_scores_24h
UNION ALL
SELECT 'mv_hourly_block_accuracy', COUNT(*) FROM mv_hourly_block_accuracy
UNION ALL
SELECT 'mv_daily_score_stats', COUNT(*) FROM mv_daily_score_stats
UNION ALL
SELECT 'mv_agent_performance', COUNT(*) FROM mv_agent_performance;

-- ============================================================================
-- END OF MIGRATION 007
-- Run migration 999 for rollback procedures
-- ============================================================================
