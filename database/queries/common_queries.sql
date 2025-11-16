-- Common Queries for ICT Prediction Model Database
-- Use these queries for debugging, monitoring, and validation

-- ============================================================================
-- SECTION 1: LATEST DATA QUERIES (Dashboard Display)
-- ============================================================================

-- Get the latest OHLC bar
SELECT * FROM ohlc_data
WHERE instrument = 'NQ=F'
ORDER BY timestamp DESC LIMIT 1;

-- Get latest 10 OHLC bars (10 minutes of 1-minute data)
SELECT
    timestamp,
    open, high, low, close, volume
FROM ohlc_data
WHERE instrument = 'NQ=F'
ORDER BY timestamp DESC
LIMIT 10;

-- Get the latest score
SELECT
    calculation_time,
    bullish_total,
    bearish_total,
    directional_bias,
    bias_strength,
    star_rating,
    predicted_block,
    block_confidence,
    trigger_source
FROM score_history
WHERE instrument = 'NQ=F'
ORDER BY calculation_time DESC
LIMIT 1;

-- Get latest reference levels
SELECT
    level_type,
    value,
    timestamp_created
FROM reference_levels
WHERE instrument = 'NQ=F'
AND timestamp_created > DATE_TRUNC('day', NOW())
ORDER BY level_type;

-- Get latest Fibonacci pivots
SELECT
    timeframe,
    pp, r1, r2, r3, s1, s2, s3,
    valid_from
FROM fibonacci_pivots
WHERE instrument = 'NQ=F'
ORDER BY valid_from DESC, timeframe DESC
LIMIT 2;

-- ============================================================================
-- SECTION 2: TIME-RANGE QUERIES (Historical Data)
-- ============================================================================

-- Get all OHLC data for the last 24 hours
SELECT
    timestamp,
    open, high, low, close, volume
FROM ohlc_data
WHERE instrument = 'NQ=F'
AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Get all scores for the last 24 hours
SELECT
    calculation_time,
    bullish_total,
    bearish_total,
    directional_bias,
    bias_strength,
    execution_time_ms,
    data_completeness_percent
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours'
ORDER BY calculation_time DESC;

-- Get hourly block data for the last 24 hours
SELECT
    hour_start,
    block_number,
    block_open, block_high, block_low, block_close,
    block_volume,
    bias_direction
FROM hourly_blocks
WHERE instrument = 'NQ=F'
AND hour_start > NOW() - INTERVAL '24 hours'
ORDER BY hour_start DESC, block_number;

-- Get recent liquidity events (last 12 hours)
SELECT
    timestamp,
    event_type,
    level,
    quality_factor,
    hold_duration_minutes
FROM liquidity_events
WHERE instrument = 'NQ=F'
AND timestamp > NOW() - INTERVAL '12 hours'
ORDER BY timestamp DESC;

-- Get recent FVG zones (unfilled in last 24 hours)
SELECT
    timestamp_created,
    start_price,
    end_price,
    filled,
    timestamp_filled
FROM fvg_zones
WHERE instrument = 'NQ=F'
AND timestamp_created > NOW() - INTERVAL '24 hours'
ORDER BY timestamp_created DESC;

-- ============================================================================
-- SECTION 3: COMPONENT ANALYSIS (Score Breakdown)
-- ============================================================================

-- Extract bullish components from latest 10 scores
SELECT
    calculation_time,
    bullish_total,
    (bullish_components->>'htf_bias')::numeric as htf_bias,
    (bullish_components->>'kill_zone')::numeric as kill_zone,
    (bullish_components->>'pd_array')::numeric as pd_array,
    (bullish_components->>'liquidity')::numeric as liquidity,
    (bullish_components->>'structure')::numeric as structure,
    (bullish_components->>'equilibrium')::numeric as equilibrium
FROM score_history
WHERE instrument = 'NQ=F'
ORDER BY calculation_time DESC
LIMIT 10;

-- Extract bearish components from latest 10 scores
SELECT
    calculation_time,
    bearish_total,
    (bearish_components->>'htf_bias')::numeric as htf_bias,
    (bearish_components->>'kill_zone')::numeric as kill_zone,
    (bearish_components->>'pd_array')::numeric as pd_array,
    (bearish_components->>'liquidity')::numeric as liquidity,
    (bearish_components->>'structure')::numeric as structure,
    (bearish_components->>'equilibrium')::numeric as equilibrium
FROM score_history
WHERE instrument = 'NQ=F'
ORDER BY calculation_time DESC
LIMIT 10;

-- Average component values over last 24 hours
SELECT
    ROUND(AVG((bullish_components->>'htf_bias')::numeric), 2) as avg_bullish_htf,
    ROUND(AVG((bullish_components->>'kill_zone')::numeric), 2) as avg_bullish_kz,
    ROUND(AVG((bearish_components->>'htf_bias')::numeric), 2) as avg_bearish_htf,
    ROUND(AVG((bearish_components->>'kill_zone')::numeric), 2) as avg_bearish_kz,
    COUNT(*) as total_scores
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours';

-- ============================================================================
-- SECTION 4: QUALITY ANALYSIS (Elite Scores)
-- ============================================================================

-- Find all elite-rated scores in the last 7 days
SELECT
    calculation_time,
    bullish_total,
    bearish_total,
    directional_bias,
    star_rating,
    predicted_block,
    block_confidence
FROM score_history
WHERE instrument = 'NQ=F'
AND bias_strength = 'ELITE'
AND calculation_time > NOW() - INTERVAL '7 days'
ORDER BY calculation_time DESC;

-- Count scores by bias strength (last 24 hours)
SELECT
    bias_strength,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as percentage
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours'
GROUP BY bias_strength
ORDER BY count DESC;

-- Distribution of directional bias (last 24 hours)
SELECT
    directional_bias,
    COUNT(*) as count,
    ROUND(AVG(bullish_total), 2) as avg_bullish,
    ROUND(AVG(bearish_total), 2) as avg_bearish
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours'
GROUP BY directional_bias
ORDER BY count DESC;

-- ============================================================================
-- SECTION 5: BLOCK PREDICTION VALIDATION
-- ============================================================================

-- Get all block predictions (last 24 hours)
SELECT
    prediction_time,
    predicted_block,
    confidence,
    actual_block,
    prediction_correct
FROM block_predictions
WHERE instrument = 'NQ=F'
AND prediction_time > NOW() - INTERVAL '24 hours'
ORDER BY prediction_time DESC;

-- Block prediction accuracy statistics
SELECT
    block_number,
    COUNT(*) as total,
    SUM(CASE WHEN prediction_correct THEN 1 ELSE 0 END) as correct,
    ROUND(AVG(CASE WHEN prediction_correct THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy_pct,
    ROUND(AVG(confidence), 2) as avg_confidence
FROM block_predictions
WHERE instrument = 'NQ=F'
AND prediction_time > NOW() - INTERVAL '7 days'
GROUP BY block_number
ORDER BY block_number;

-- ============================================================================
-- SECTION 6: ERROR MONITORING
-- ============================================================================

-- Get recent errors (last 24 hours)
SELECT
    timestamp,
    agent_name,
    error_type,
    error_message
FROM error_log
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Error summary by agent (last 7 days)
SELECT
    agent_name,
    error_type,
    COUNT(*) as error_count,
    MAX(timestamp) as latest_error
FROM error_log
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY agent_name, error_type
ORDER BY agent_name, error_count DESC;

-- Agent error rate (last 24 hours, assuming ~480 scores/day)
SELECT
    'Agent2_ScoreCalculator' as agent,
    480 as expected_executions,
    COUNT(*) as error_count,
    ROUND((COUNT()::numeric / 480) * 100, 2) as error_rate_pct
FROM error_log
WHERE agent_name = 'Agent2_ScoreCalculator'
AND timestamp > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT
    'Agent1_DataCollector',
    24,  -- 24 hourly cycles
    COUNT(*),
    ROUND((COUNT()::numeric / 24) * 100, 2)
FROM error_log
WHERE agent_name = 'Agent1_DataCollector'
AND timestamp > NOW() - INTERVAL '24 hours';

-- ============================================================================
-- SECTION 7: PERFORMANCE METRICS
-- ============================================================================

-- Average execution time for Agent 2 (last 24 hours)
SELECT
    COUNT(*) as total_executions,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_ms,
    MIN(execution_time_ms) as min_execution_ms,
    MAX(execution_time_ms) as max_execution_ms,
    ROUND(STDDEV(execution_time_ms), 2) as stddev_execution_ms
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours';

-- Data completeness analysis (last 24 hours)
SELECT
    data_completeness_percent,
    COUNT(*) as score_count,
    ROUND(AVG(bullish_total), 2) as avg_bullish
FROM score_history
WHERE instrument = 'NQ=F'
AND calculation_time > NOW() - INTERVAL '24 hours'
GROUP BY data_completeness_percent
ORDER BY data_completeness_percent DESC;

-- Query execution performance (if pg_stat_statements enabled)
SELECT
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_time_ms,
    ROUND(max_exec_time::numeric, 2) as max_time_ms
FROM pg_stat_statements
WHERE query LIKE '%score_history%'
OR query LIKE '%ohlc_data%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- ============================================================================
-- SECTION 8: DATA VOLUME CHECKS
-- ============================================================================

-- Count of rows per table
SELECT
    'ohlc_data' as table_name,
    COUNT(*) as row_count
FROM ohlc_data
UNION ALL
SELECT 'score_history', COUNT(*) FROM score_history
UNION ALL
SELECT 'liquidity_events', COUNT(*) FROM liquidity_events
UNION ALL
SELECT 'market_structure', COUNT(*) FROM market_structure
UNION ALL
SELECT 'fvg_zones', COUNT(*) FROM fvg_zones
UNION ALL
SELECT 'hourly_blocks', COUNT(*) FROM hourly_blocks
UNION ALL
SELECT 'reference_levels', COUNT(*) FROM reference_levels
UNION ALL
SELECT 'fibonacci_pivots', COUNT(*) FROM fibonacci_pivots
UNION ALL
SELECT 'block_predictions', COUNT(*) FROM block_predictions
UNION ALL
SELECT 'error_log', COUNT(*) FROM error_log;

-- Database size breakdown
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- SECTION 9: DATA CLEANUP (Safe to Run)
-- ============================================================================

-- Preview: Errors older than 7 days (not deleted)
SELECT COUNT(*) as would_delete_errors
FROM error_log
WHERE timestamp < NOW() - INTERVAL '7 days';

-- Preview: OHLC data older than 30 days (would be deleted)
-- Note: Hypertable retention policies handle this automatically
-- SELECT COUNT(*) as would_delete_ohlc
-- FROM ohlc_data
-- WHERE timestamp < NOW() - INTERVAL '30 days';

-- ============================================================================
-- SECTION 10: MATERIALIZED VIEW CHECKS
-- ============================================================================

-- Verify materialized views exist and have data
SELECT
    'mv_latest_reference_levels' as view_name,
    COUNT(*) as row_count
FROM mv_latest_reference_levels
WHERE instrument = 'NQ=F'
UNION ALL
SELECT 'mv_latest_fibonacci_pivots', COUNT(*) FROM mv_latest_fibonacci_pivots WHERE instrument = 'NQ=F'
UNION ALL
SELECT 'mv_recent_scores_24h', COUNT(*) FROM mv_recent_scores_24h WHERE instrument = 'NQ=F'
UNION ALL
SELECT 'mv_hourly_block_accuracy', COUNT(*) FROM mv_hourly_block_accuracy
UNION ALL
SELECT 'mv_daily_score_stats', COUNT(*) FROM mv_daily_score_stats WHERE instrument = 'NQ=F'
UNION ALL
SELECT 'mv_agent_performance', COUNT(*) FROM mv_agent_performance;

-- Get recent scores summary from materialized view (faster for dashboard)
SELECT
    calculation_time,
    bullish_total,
    bearish_total,
    directional_bias,
    bias_strength,
    bullish_htf_bias,
    bullish_kill_zone,
    bullish_pd_array
FROM mv_recent_scores_24h
WHERE instrument = 'NQ=F'
ORDER BY calculation_time DESC
LIMIT 5;
