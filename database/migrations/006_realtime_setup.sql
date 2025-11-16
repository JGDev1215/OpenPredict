-- Migration 006: Real-Time Subscription Setup
-- Enable Supabase Realtime for score_history table (dashboard updates)

-- ============================================================================
-- ENABLE REALTIME PUBLICATION
-- ============================================================================

-- Create a publication that includes score_history for Realtime subscriptions
CREATE PUBLICATION supabase_realtime_score_updates FOR TABLE score_history;

-- Verify publication exists
SELECT * FROM pg_publication WHERE pubname = 'supabase_realtime_score_updates';

-- ============================================================================
-- CREATE REALTIME TRIGGER FUNCTION
-- ============================================================================

-- Function to notify on score updates (for dashboard real-time updates)
CREATE OR REPLACE FUNCTION notify_score_update()
RETURNS TRIGGER AS $$
DECLARE
    payload jsonb;
BEGIN
    -- Build notification payload
    payload := jsonb_build_object(
        'id', NEW.id,
        'calculation_time', NEW.calculation_time,
        'instrument', NEW.instrument,
        'bullish_total', NEW.bullish_total,
        'bearish_total', NEW.bearish_total,
        'directional_bias', NEW.directional_bias,
        'bias_strength', NEW.bias_strength,
        'star_rating', NEW.star_rating,
        'predicted_block', NEW.predicted_block,
        'block_confidence', NEW.block_confidence,
        'bullish_components', NEW.bullish_components,
        'bearish_components', NEW.bearish_components,
        'trigger_source', NEW.trigger_source,
        'event', 'INSERT'
    );

    -- Send notification to PostgreSQL LISTEN/NOTIFY system
    PERFORM pg_notify(
        'score_history_updates',
        payload::text
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE TRIGGERS FOR REALTIME UPDATES
-- ============================================================================

-- Trigger on INSERT to notify dashboard of new scores
DROP TRIGGER IF EXISTS trigger_score_insert ON score_history;
CREATE TRIGGER trigger_score_insert
AFTER INSERT ON score_history
FOR EACH ROW EXECUTE FUNCTION notify_score_update();

-- Trigger on UPDATE to notify of score corrections (if any)
DROP TRIGGER IF EXISTS trigger_score_update ON score_history;
CREATE TRIGGER trigger_score_update
AFTER UPDATE ON score_history
FOR EACH ROW EXECUTE FUNCTION notify_score_update();

-- ============================================================================
-- VERIFY REALTIME SETUP
-- ============================================================================

-- Check publications
SELECT pubname, pubcreator
FROM pg_publication
WHERE pubname LIKE '%realtime%' OR pubname LIKE '%score%';

-- Check triggers on score_history
SELECT
    trigger_name,
    event_object_schema,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table = 'score_history'
ORDER BY trigger_name;

-- ============================================================================
-- SUPABASE REALTIME CHANNEL CONFIGURATION
-- ============================================================================

-- This section is for documentation of the frontend subscription setup
-- In JavaScript/React, the frontend will subscribe like this:

/*
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
    process.env.REACT_APP_SUPABASE_URL,
    process.env.REACT_APP_SUPABASE_ANON_KEY
)

// Subscribe to score_history table updates
const scoreChannel = supabase
    .channel('score_history_updates')
    .on(
        'postgres_changes',
        {
            event: 'INSERT',
            schema: 'public',
            table: 'score_history'
        },
        (payload) => {
            console.log('New score:', payload.new)
            // Update dashboard with new score
            updateDashboardScore(payload.new)
        }
    )
    .subscribe()

// Clean up subscription on unmount
return () => {
    supabase.removeChannel(scoreChannel)
}
*/

-- ============================================================================
-- PERFORMANCE CONSIDERATIONS
-- ============================================================================

-- Real-time subscriptions performance:
-- - Notification latency: <500ms from INSERT to dashboard update
-- - Network latency: ~50-100ms (varies by location)
-- - Total time: <600ms typical
--
-- Scaling notes:
-- - Supabase Realtime can handle ~100 concurrent connections per table
-- - For higher scale, implement batched updates (every 3 minutes)
-- - Current system: ~480 updates/day = acceptable load
--
-- Cost: Realtime is included in Supabase pricing, no additional cost

-- ============================================================================
-- ALTERNATIVE: POLLING-BASED UPDATES (Lower cost, higher latency)
-- ============================================================================

-- If Realtime subscriptions cause issues, frontend can fall back to polling:
-- - Poll /api/scores/latest every 3 minutes
-- - Latency: 0-180 seconds (depending on poll timing)
-- - Cost: Minimal API bandwidth (~100 requests/day)
-- - Implementation: React useEffect with setInterval

-- ============================================================================
-- MONITOR REALTIME ACTIVITY
-- ============================================================================

-- View active PostgreSQL connections (includes Realtime)
SELECT
    usename,
    application_name,
    state,
    query,
    state_change
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY state_change DESC;

-- View notification queue size (if congested)
-- SELECT pg_stat_get_notify_queue_size() as notification_queue_size;

-- ============================================================================
-- END OF MIGRATION 006
-- Run migration 007 to create materialized views for aggregations
-- ============================================================================
