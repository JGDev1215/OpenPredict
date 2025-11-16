Based on comprehensive analysis with specialized agents, here's the 
     implementation roadmap:

     Phase 1: Database Foundation (Week 1)

     - Create Supabase project and enable TimescaleDB extension
     - Deploy 8 SQL migration files:
       - 10 tables (ohlc_data, score_history, reference_levels, 
     fibonacci_pivots, liquidity_events, market_structure, fvg_zones, 
     hourly_blocks, block_predictions, error_log)
       - 6 TimescaleDB hypertables with 1-day/7-day chunk intervals
       - Performance indexes (B-tree + BRIN) for sub-200ms queries
       - 30-day retention policies with auto-cleanup
       - 7-day compression policies (save 60% storage)
       - Real-time subscriptions for score_history table
       - 3 materialized views for common aggregations
     - Verify setup with performance tests

     Phase 2: Agent 1 - Data Collector (Week 1-2)

     Create /agent1 directory with:
     - Core Components:
       - YahooFinanceFetcher with retry logic (3 attempts, exponential backoff)
       - SupabaseOHLCRepository for batch upserts
       - OHLCCache with 50-second TTL
       - TimezoneManager for ET/UTC conversion
       - MarketHoursChecker for holiday detection
     - 6 Calculators/Detectors:
       - ReferenceLevelCalculator (8 levels: weekly/daily/NY opens, Asian H/L, 
     prev day H/L)
       - FibonacciPivotCalculator (weekly + daily S1-S3, PP, R1-R3)
       - LiquidityEventDetector (raids/sweeps with quality scoring)
       - FVGDetector (15-min Fair Value Gaps)
       - HourlyBlockSegmenter (7 blocks per hour)
       - MarketStructureDetector (BOS/CHoCH patterns)
     - APScheduler Integration:
       - 60-second interval with max_instances=1
       - Target: <8s execution time per cycle
       - Error logging to Supabase error_log table

     Phase 3: Agent 2 - Score Calculator (Week 2)

     Create /agent2 directory with:
     - 6 Weighted Components:
       - HTFBiasCalculator (30%): Price vs 8 reference levels with distance 
     decay
       - KillZoneCalculator (20%): Session timing with day multipliers
       - PDArrayCalculator (25%): Fib pivots + FVG confluence (1.3-1.5x 
     multipliers)
       - LiquidityCalculator (15%): Recent raids with hold bonuses
       - StructureCalculator (10%): Market structure breaks + displacement
       - EquilibriumCalculator (±5%): Multi-timeframe alignment bonus/penalty
     - Dual-Direction Scoring:
       - Independent bullish and bearish scores (0-100 range)
       - Directional bias calculation (BULLISH/BEARISH/NEUTRAL)
       - Bias strength (ELITE/HIGH/ACCEPTABLE/MARGINAL/POOR)
       - Star rating (1-5 stars)
     - Block Prediction Engine:
       - 3 decision trees (Kill Zone Priority, Liquidity Targeting, Structure 
     Confluence)
       - Ensemble voting for blocks 1-7
       - Confidence scoring (33%/66%/100% agreement)
     - Triggers:
       - APScheduler: 3-minute cron (*/3 * * * *)
       - Manual API: /scores/calculate endpoint
       - Target: <3s execution time

     Phase 4: FastAPI Backend (Week 3)

     - Setup FastAPI project with 5 route modules
     - Implement 18 REST endpoints:
       - /scores/latest - Current dual scores
       - /scores/history - Historical with pagination
       - /scores/calculate - Manual trigger
       - /market/price, /market/levels, /market/pivots
       - /health - Service monitoring
     - Add CORS, rate limiting (slowapi), Pydantic validation
     - Deploy to Render.com (3 services: API + Agent1 + Agent2)

     Phase 5: React Dashboard (Week 4)

     - React + TypeScript + Bootstrap 5
     - Components: DualScoreDisplay, ComponentBreakdown, BlockTimeline
     - Supabase real-time subscriptions (3-min updates)
     - Responsive mobile layout
     - Target: <1MB bundle, <2s initial load

     Phase 6: Testing & Deployment (Week 4-5)

     - Unit tests for all 6 scoring components (pytest)
     - Integration tests for Agent 1 → Supabase → Agent 2 pipeline
     - Backtest on 7 days historical data
     - Performance validation (<8s Agent1, <3s Agent2, <200ms API)
     - Production deployment with health monitoring

     Success Criteria

     ✅ Agent 1: >95% fetch success rate, <8s execution
     ✅ Agent 2: >98% calculation success, <3s execution
     ✅ API: <200ms response for /scores/latest
     ✅ Dashboard: Real-time updates via Supabase
     ✅ Block predictions: >70% accuracy (7-day validation)
     ✅ System uptime: <1 hour downtime per week