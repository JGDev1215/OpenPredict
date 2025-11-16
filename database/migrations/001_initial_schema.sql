-- Migration 001: Initial Schema Creation
-- Creates all 10 core tables for ICT Quantitative Prediction Model
-- TimescaleDB extension must be enabled before running this migration

-- ============================================================================
-- ENABLE EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- CREATE ENUM TYPES
-- ============================================================================

CREATE TYPE direction_enum AS ENUM ('BULLISH', 'BEARISH', 'NEUTRAL');
CREATE TYPE rating_enum AS ENUM ('ELITE', 'HIGH', 'ACCEPTABLE', 'MARGINAL', 'POOR');
CREATE TYPE event_type_enum AS ENUM ('raid', 'sweep', 'hold', 'reversal');
CREATE TYPE structure_type_enum AS ENUM ('BOS', 'CHOCH', 'break', 'continuation');
CREATE TYPE trigger_source_enum AS ENUM ('auto_timer', 'manual_button', 'api_call');

-- ============================================================================
-- TABLE 1: OHLC_DATA - Raw 1-minute OHLC from yfinance
-- ============================================================================

CREATE TABLE IF NOT EXISTS ohlc_data (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT ohlc_high_low_valid CHECK (high >= low),
    CONSTRAINT ohlc_price_valid CHECK (open > 0 AND high > 0 AND low > 0 AND close > 0),
    CONSTRAINT ohlc_volume_valid CHECK (volume >= 0),

    -- Composite primary key
    PRIMARY KEY (timestamp, instrument)
);

COMMENT ON TABLE ohlc_data IS 'Raw 1-minute OHLC bars from yfinance for NQ=F. ~1,440 rows/day. Will be converted to hypertable.';
COMMENT ON COLUMN ohlc_data.timestamp IS 'Bar close time in UTC';
COMMENT ON COLUMN ohlc_data.volume IS 'Total volume for the 1-minute bar';

-- ============================================================================
-- TABLE 2: REFERENCE_LEVELS - 8 Reference levels (weekly/daily/NY opens, etc)
-- ============================================================================

CREATE TABLE IF NOT EXISTS reference_levels (
    id BIGSERIAL PRIMARY KEY,
    timestamp_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    instrument VARCHAR(20) NOT NULL,
    level_type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,

    -- Constraints
    CONSTRAINT ref_level_type_valid CHECK (level_type IN (
        'weekly_open', 'daily_open', 'asian_high', 'asian_low',
        'london_open', 'ny_midnight_open', 'prev_day_high', 'prev_day_low'
    )),
    CONSTRAINT ref_level_price_valid CHECK (value > 0),

    -- Unique constraint: One level per type per instrument per timestamp
    UNIQUE (instrument, level_type, DATE(timestamp_created))
);

COMMENT ON TABLE reference_levels IS 'Calculated reference levels updated every cycle. ~8 active records per instrument.';
COMMENT ON COLUMN reference_levels.level_type IS 'Type of reference level (weekly_open, daily_open, etc)';
COMMENT ON COLUMN reference_levels.value IS 'Price level value';

-- ============================================================================
-- TABLE 3: FIBONACCI_PIVOTS - Weekly and daily Fibonacci pivots
-- ============================================================================

CREATE TABLE IF NOT EXISTS fibonacci_pivots (
    id BIGSERIAL PRIMARY KEY,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    instrument VARCHAR(20) NOT NULL,
    timeframe VARCHAR(20) NOT NULL,
    pp NUMERIC(10, 2) NOT NULL,
    r1 NUMERIC(10, 2) NOT NULL,
    r2 NUMERIC(10, 2) NOT NULL,
    r3 NUMERIC(10, 2) NOT NULL,
    s1 NUMERIC(10, 2) NOT NULL,
    s2 NUMERIC(10, 2) NOT NULL,
    s3 NUMERIC(10, 2) NOT NULL,

    -- Constraints
    CONSTRAINT fib_timeframe_valid CHECK (timeframe IN ('weekly', 'daily')),
    CONSTRAINT fib_price_valid CHECK (pp > 0 AND r1 > 0 AND r2 > 0 AND r3 > 0 AND s1 > 0 AND s2 > 0 AND s3 > 0),

    -- Unique: One pivot set per timeframe per instrument per day
    UNIQUE (instrument, timeframe, DATE(valid_from))
);

COMMENT ON TABLE fibonacci_pivots IS 'Fibonacci-based pivot points. Updated once per period. ~2 active records per instrument.';
COMMENT ON COLUMN fibonacci_pivots.timeframe IS 'weekly or daily';

-- ============================================================================
-- TABLE 4: LIQUIDITY_EVENTS - Raids and sweeps detection
-- ============================================================================

CREATE TABLE IF NOT EXISTS liquidity_events (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    event_type event_type_enum NOT NULL,
    level NUMERIC(10, 2) NOT NULL,
    quality_factor NUMERIC(3, 2) NOT NULL DEFAULT 1.0,
    hold_duration_minutes INT DEFAULT 0,

    -- Constraints
    CONSTRAINT liquidity_quality_valid CHECK (quality_factor >= 0 AND quality_factor <= 1.0),
    CONSTRAINT liquidity_hold_valid CHECK (hold_duration_minutes >= 0),
    CONSTRAINT liquidity_level_valid CHECK (level > 0),

    PRIMARY KEY (timestamp, instrument, event_type)
);

COMMENT ON TABLE liquidity_events IS 'Detected raids and sweeps. ~50-100 events/day. Will be converted to hypertable.';
COMMENT ON COLUMN liquidity_events.quality_factor IS 'Quality score 0-1.0 (1.0 = clean sweep)';
COMMENT ON COLUMN liquidity_events.hold_duration_minutes IS 'How long level held after raid/sweep';

-- ============================================================================
-- TABLE 5: MARKET_STRUCTURE - Breaks and displacements
-- ============================================================================

CREATE TABLE IF NOT EXISTS market_structure (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    structure_type structure_type_enum NOT NULL,
    direction direction_enum NOT NULL,
    level NUMERIC(10, 2),
    displacement_pips INT DEFAULT 0,

    -- Constraints
    CONSTRAINT structure_displacement_valid CHECK (displacement_pips >= 0),

    PRIMARY KEY (timestamp, instrument)
);

COMMENT ON TABLE market_structure IS 'Market structure breaks (BOS/CHoCH). ~30-50 breaks/day. Will be converted to hypertable.';
COMMENT ON COLUMN market_structure.displacement_pips IS 'Size of move in pips';

-- ============================================================================
-- TABLE 6: FVG_ZONES - Fair Value Gap detection (15-min timeframe)
-- ============================================================================

CREATE TABLE IF NOT EXISTS fvg_zones (
    id BIGSERIAL,
    timestamp_created TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    start_price NUMERIC(10, 2) NOT NULL,
    end_price NUMERIC(10, 2) NOT NULL,
    timeframe VARCHAR(20) NOT NULL DEFAULT '15m',
    filled BOOLEAN DEFAULT FALSE,
    timestamp_filled TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT fvg_price_valid CHECK (start_price > 0 AND end_price > 0),
    CONSTRAINT fvg_filled_logic CHECK (
        (filled = FALSE AND timestamp_filled IS NULL) OR
        (filled = TRUE AND timestamp_filled IS NOT NULL)
    ),

    PRIMARY KEY (timestamp_created, instrument)
);

COMMENT ON TABLE fvg_zones IS 'Fair Value Gaps on 15-minute timeframe. ~20-40 FVGs/day. Will be converted to hypertable.';
COMMENT ON COLUMN fvg_zones.filled IS 'TRUE if FVG has been filled (price entered the gap)';

-- ============================================================================
-- TABLE 7: HOURLY_BLOCKS - 7-block segmentation per hour
-- ============================================================================

CREATE TABLE IF NOT EXISTS hourly_blocks (
    id BIGSERIAL,
    hour_start TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    block_number SMALLINT NOT NULL,
    block_open NUMERIC(10, 2) NOT NULL,
    block_high NUMERIC(10, 2) NOT NULL,
    block_low NUMERIC(10, 2) NOT NULL,
    block_close NUMERIC(10, 2) NOT NULL,
    block_volume BIGINT NOT NULL DEFAULT 0,
    bias_direction direction_enum DEFAULT 'NEUTRAL',

    -- Constraints
    CONSTRAINT block_number_valid CHECK (block_number >= 1 AND block_number <= 7),
    CONSTRAINT block_price_valid CHECK (
        block_open > 0 AND block_high > 0 AND block_low > 0 AND block_close > 0
    ),
    CONSTRAINT block_high_low_valid CHECK (block_high >= block_low),
    CONSTRAINT block_volume_valid CHECK (block_volume >= 0),

    PRIMARY KEY (hour_start, instrument, block_number)
);

COMMENT ON TABLE hourly_blocks IS 'Hourly block segmentation (7 blocks/hour). 168 blocks/day. Will be converted to hypertable.';
COMMENT ON COLUMN hourly_blocks.block_number IS 'Block number 1-7 within the hour';

-- ============================================================================
-- TABLE 8: SCORE_HISTORY - Agent 2 output (CRITICAL for real-time subscriptions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS score_history (
    id BIGSERIAL,
    calculation_time TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    bullish_total NUMERIC(5, 2) NOT NULL,
    bearish_total NUMERIC(5, 2) NOT NULL,
    directional_bias direction_enum NOT NULL,
    bias_strength rating_enum NOT NULL,
    star_rating SMALLINT NOT NULL,
    predicted_block SMALLINT,
    block_confidence NUMERIC(5, 2),
    trigger_source trigger_source_enum NOT NULL DEFAULT 'auto_timer',

    -- Component breakdown (JSONB for flexibility)
    bullish_components JSONB NOT NULL DEFAULT '{
        "htf_bias": 0.0,
        "kill_zone": 0.0,
        "pd_array": 0.0,
        "liquidity": 0.0,
        "structure": 0.0,
        "equilibrium": 0.0
    }'::jsonb,
    bearish_components JSONB NOT NULL DEFAULT '{
        "htf_bias": 0.0,
        "kill_zone": 0.0,
        "pd_array": 0.0,
        "liquidity": 0.0,
        "structure": 0.0,
        "equilibrium": 0.0
    }'::jsonb,

    -- Metadata
    execution_time_ms INT,
    data_completeness_percent SMALLINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT score_total_valid CHECK (bullish_total >= 0 AND bullish_total <= 105),
    CONSTRAINT score_bearish_valid CHECK (bearish_total >= 0 AND bearish_total <= 105),
    CONSTRAINT block_number_valid CHECK (predicted_block IS NULL OR (predicted_block >= 1 AND predicted_block <= 7)),
    CONSTRAINT block_confidence_valid CHECK (block_confidence IS NULL OR (block_confidence >= 0 AND block_confidence <= 100)),
    CONSTRAINT star_rating_valid CHECK (star_rating >= 1 AND star_rating <= 5),
    CONSTRAINT execution_time_valid CHECK (execution_time_ms IS NULL OR execution_time_ms > 0),
    CONSTRAINT data_completeness_valid CHECK (data_completeness_percent >= 0 AND data_completeness_percent <= 100),

    PRIMARY KEY (calculation_time, instrument)
);

COMMENT ON TABLE score_history IS 'Agent 2 scoring output. ~480 rows/day. CRITICAL: Real-time subscriptions enabled. Will be converted to hypertable.';
COMMENT ON COLUMN score_history.bullish_total IS 'Total bullish score 0-100 (plus ±5 equilibrium bonus)';
COMMENT ON COLUMN score_history.bearish_total IS 'Total bearish score 0-100 (plus ±5 equilibrium bonus)';
COMMENT ON COLUMN score_history.bullish_components IS 'JSONB with individual component scores for bullish';
COMMENT ON COLUMN score_history.bearish_components IS 'JSONB with individual component scores for bearish';

-- ============================================================================
-- TABLE 9: BLOCK_PREDICTIONS - Hourly block predictions with accuracy tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS block_predictions (
    id BIGSERIAL PRIMARY KEY,
    prediction_time TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    predicted_block SMALLINT NOT NULL,
    confidence NUMERIC(5, 2) NOT NULL,
    actual_block SMALLINT,
    prediction_correct BOOLEAN,

    -- Constraints
    CONSTRAINT pred_block_valid CHECK (predicted_block >= 1 AND predicted_block <= 7),
    CONSTRAINT actual_block_valid CHECK (actual_block IS NULL OR (actual_block >= 1 AND actual_block <= 7)),
    CONSTRAINT confidence_valid CHECK (confidence >= 0 AND confidence <= 100),
    CONSTRAINT prediction_correct_logic CHECK (
        (actual_block IS NULL AND prediction_correct IS NULL) OR
        (actual_block IS NOT NULL AND prediction_correct IS NOT NULL)
    ),

    -- Unique per hour
    UNIQUE (instrument, DATE_TRUNC('hour', prediction_time))
);

COMMENT ON TABLE block_predictions IS 'Hourly block predictions for validation. ~24 predictions/day.';
COMMENT ON COLUMN block_predictions.prediction_correct IS 'TRUE if predicted_block matched actual_block';

-- ============================================================================
-- TABLE 10: ERROR_LOG - Agent error tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS error_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_name VARCHAR(50) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,

    -- Constraints
    CONSTRAINT agent_name_valid CHECK (agent_name IN ('Agent1_DataCollector', 'Agent2_ScoreCalculator', 'API_Service'))
);

COMMENT ON TABLE error_log IS 'Agent error tracking. Auto-cleaned after 7 days. Retention: 7 days max.';

-- ============================================================================
-- CREATE INDEXES (Before Hypertable Conversion)
-- ============================================================================

-- OHLC_DATA indexes
CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp_instrument ON ohlc_data (timestamp DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_ohlc_instrument_timestamp ON ohlc_data (instrument, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp_brin ON ohlc_data USING BRIN (timestamp);

-- REFERENCE_LEVELS indexes
CREATE INDEX IF NOT EXISTS idx_ref_levels_instrument_type ON reference_levels (instrument, level_type);
CREATE INDEX IF NOT EXISTS idx_ref_levels_timestamp ON reference_levels (timestamp_created DESC);

-- LIQUIDITY_EVENTS indexes
CREATE INDEX IF NOT EXISTS idx_liquidity_timestamp_instrument ON liquidity_events (timestamp DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_liquidity_timestamp_brin ON liquidity_events USING BRIN (timestamp);
CREATE INDEX IF NOT EXISTS idx_liquidity_event_type ON liquidity_events (event_type, timestamp DESC);

-- MARKET_STRUCTURE indexes
CREATE INDEX IF NOT EXISTS idx_structure_timestamp_instrument ON market_structure (timestamp DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_structure_timestamp_brin ON market_structure USING BRIN (timestamp);
CREATE INDEX IF NOT EXISTS idx_structure_type ON market_structure (structure_type, direction);

-- FVG_ZONES indexes
CREATE INDEX IF NOT EXISTS idx_fvg_timestamp_instrument ON fvg_zones (timestamp_created DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_fvg_timestamp_brin ON fvg_zones USING BRIN (timestamp_created);
CREATE INDEX IF NOT EXISTS idx_fvg_filled ON fvg_zones (filled, timestamp_created DESC);

-- HOURLY_BLOCKS indexes
CREATE INDEX IF NOT EXISTS idx_blocks_hour_start_instrument ON hourly_blocks (hour_start DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_blocks_hour_start_brin ON hourly_blocks USING BRIN (hour_start);
CREATE INDEX IF NOT EXISTS idx_blocks_number ON hourly_blocks (block_number, hour_start DESC);

-- SCORE_HISTORY indexes (CRITICAL for real-time + recent queries)
CREATE INDEX IF NOT EXISTS idx_score_timestamp_instrument ON score_history (calculation_time DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_score_timestamp_brin ON score_history USING BRIN (calculation_time);
CREATE INDEX IF NOT EXISTS idx_score_latest ON score_history (instrument, calculation_time DESC)
    WHERE calculation_time > NOW() - INTERVAL '1 hour';
CREATE INDEX IF NOT EXISTS idx_score_components_bullish ON score_history USING GIN (bullish_components);
CREATE INDEX IF NOT EXISTS idx_score_components_bearish ON score_history USING GIN (bearish_components);

-- BLOCK_PREDICTIONS indexes
CREATE INDEX IF NOT EXISTS idx_predictions_time_instrument ON block_predictions (prediction_time DESC, instrument);
CREATE INDEX IF NOT EXISTS idx_predictions_correct ON block_predictions (prediction_correct, instrument);

-- ERROR_LOG indexes
CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_log (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_agent ON error_log (agent_name, timestamp DESC);

-- ============================================================================
-- END OF MIGRATION 001
-- ============================================================================

-- Run migration 002 to convert tables to hypertables and apply specific optimizations
