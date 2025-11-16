# OpenPredict - Product Development Roadmap
**ICT Quantitative Prediction Model**

**Version:** 1.0
**Last Updated:** November 16, 2025
**Project Objective:** Build a real-time dual-direction (bullish/bearish) scoring system for ICT trading setups with workability as the primary goal before scalability and security.

---

## 📊 Executive Summary

### Vision
OpenPredict transforms qualitative ICT trading concepts into quantitative 0-100 scores for both bullish and bearish setups, updating automatically every 3 minutes with real-time data from yfinance.

### Core Philosophy
**Workability First** → **Functionality** → **Scalability** → **Security**
Focus on getting a working MVP that demonstrates value before optimizing for scale.

### Key Metrics
- **Target Users:** Solo traders, prop firm traders, ICT students
- **Data Refresh:** Every 60 seconds (Agent 1), Every 3 minutes (Agent 2)
- **Response Time:** <200ms for API calls, <3s for score generation
- **Uptime Goal:** >95% during market hours (MVP), >99% (production)

---

## ✅ Current Status (as of Nov 16, 2025)

### Completed ✓

#### Phase 1: Database Foundation (100% Complete)
- ✅ **Database Schema Design**
  - 10 tables (OHLC, scores, reference levels, pivots, liquidity, structure, FVG, blocks, predictions, errors)
  - TimescaleDB hypertables for time-series optimization
  - 30+ indexes (B-tree + BRIN) for sub-200ms queries
  - 30-day retention policies with auto-cleanup
  - 7-day compression policies (60% storage savings)
  - Real-time subscriptions for `score_history` table
  - 6 materialized views for aggregations

- ✅ **Migration Files**
  - `001_initial_schema.sql` (17KB)
  - `002_timescale_hypertables.sql` (4.7KB)
  - `003_indexes.sql` (5.3KB)
  - `004_retention_policies.sql` (6.6KB)
  - `005_compression_policies.sql` (4.7KB)
  - `006_realtime_setup.sql` (6.0KB)
  - `007_materialized_views.sql` (11KB)
  - `999_rollback.sql` (5.1KB - emergency reset)
  - `common_queries.sql` (13KB - helper queries)

- ✅ **Documentation**
  - `readme.txt` (44KB) - Complete ICT methodology & system architecture
  - `database/README.md` - Full database setup guide with performance targets
  - `DASHBOARD_UI_DESIGN.md` (65KB) - Complete UI/UX design with wireframes, components, and code snippets
  - `implementationplanv1.md` - Implementation summary
  - `draftplan.md` - Detailed 8-phase plan

### Outstanding (Not Started)

#### Phase 2: Agent 1 - Data Collector (0% Complete)
- ❌ YahooFinance API integration
- ❌ OHLC data fetcher (60-second loop)
- ❌ Reference level calculator (8 levels)
- ❌ Fibonacci pivot calculator (weekly/daily)
- ❌ Liquidity event detector
- ❌ FVG detector (15-min timeframe)
- ❌ Hourly block segmenter (7 blocks)
- ❌ Market structure detector (BOS/CHoCH)

#### Phase 3: Agent 2 - Score Calculator (0% Complete)
- ❌ HTF Bias component (30% weight)
- ❌ Kill Zone component (20% weight)
- ❌ PD Array component (25% weight)
- ❌ Liquidity component (15% weight)
- ❌ Structure component (10% weight)
- ❌ Equilibrium component (±5% bonus)
- ❌ Dual-direction scoring logic
- ❌ Block prediction engine (3 decision trees)

#### Phase 4: FastAPI Backend (0% Complete)
- ❌ API setup with 18 endpoints
- ❌ CORS, rate limiting, validation
- ❌ Service layer for business logic
- ❌ OpenAPI spec generation

#### Phase 5: React Dashboard (0% Complete)
- ❌ React + TypeScript setup
- ❌ Dual score display components
- ❌ Component breakdown grid
- ❌ Supabase real-time subscriptions
- ❌ Responsive mobile layout

#### Phase 6: Testing & Validation (0% Complete)
- ❌ Unit tests for scoring components
- ❌ Integration tests for data pipeline
- ❌ Backtest on 7 days historical data

#### Phase 7: Deployment (0% Complete)
- ❌ Supabase production setup
- ❌ Render.com deployment (API + Agents)
- ❌ Frontend deployment (Vercel/Netlify)
- ❌ Health monitoring

#### Phase 8: Documentation & Handoff (0% Complete)
- ❌ API documentation
- ❌ Operational runbook
- ❌ User guide

---

## 🗺️ Phase-by-Phase Roadmap

### Phase 1: Database Foundation ✅ **COMPLETED**

**Status:** ✅ 100% Complete
**Duration:** Week 1 (Completed)
**Objective:** Set up PostgreSQL/TimescaleDB database with optimal schema for time-series financial data

**Deliverables:**
- [x] Supabase project created
- [x] TimescaleDB extension enabled
- [x] 10 tables with constraints and validation
- [x] 6 hypertables (1-day & 7-day chunks)
- [x] 30+ indexes (B-tree + BRIN)
- [x] Retention policies (30-day auto-cleanup)
- [x] Compression policies (60% storage savings)
- [x] Real-time subscription triggers
- [x] Materialized views for aggregations
- [x] Migration files (001-007 + rollback)
- [x] Database README with setup guide

**Success Criteria:**
- ✅ All migrations execute successfully (<30 seconds)
- ✅ Query performance: Latest score <50ms, 1-day range <150ms
- ✅ Database size: ~5-8MB/month compressed
- ✅ Real-time subscriptions functional

**Dependencies:** None
**Blockers:** None

---

### Phase 2: Agent 1 - Data Collector 🚧 **NEXT UP**

**Status:** ❌ 0% Complete
**Duration:** Week 1-2 (5-10 days)
**Objective:** Build automated data collection agent that fetches OHLC data from yfinance and calculates all ICT reference levels

**Priority:** **CRITICAL** - All downstream components depend on this

**Deliverables:**

#### Core Infrastructure
- [ ] Project structure: `/agent1` directory
- [ ] Python virtual environment setup
- [ ] `requirements.txt` with dependencies:
  ```
  yfinance>=0.2.32
  supabase>=2.0.0
  pandas>=2.1.0
  python-dotenv>=1.0.0
  APScheduler>=3.10.4
  ```
- [ ] Environment configuration (`.env.example`)
- [ ] Logging setup (file + console)

#### Data Fetcher Module
- [ ] `yahoo_finance_fetcher.py`
  - Fetch 1-minute OHLC bars from yfinance
  - Retry logic (3 attempts, exponential backoff)
  - Error handling for API failures
  - Cache with 50-second TTL

#### Database Module
- [ ] `supabase_client.py`
  - Connection management
  - Batch upserts for OHLC data
  - Error logging to `error_log` table

#### Calculators (6 modules)
- [ ] `reference_level_calculator.py`
  - Weekly Open (Monday 00:00 UTC)
  - Daily Open (00:00 UTC)
  - NY Open (13:30 UTC / 08:30 ET)
  - Asian Session High/Low
  - Previous Day High/Low
  - 4H Open, 1H Open
  - Monthly Open

- [ ] `fibonacci_pivot_calculator.py`
  - Weekly pivots (S3, S2, S1, PP, R1, R2, R3)
  - Daily pivots (S3, S2, S1, PP, R1, R2, R3)
  - Formula: PP = (H + L + C) / 3
    - R1 = PP + 0.382 * (H - L)
    - S1 = PP - 0.382 * (H - L)
    - (etc. for R2, R3, S2, S3)

- [ ] `liquidity_event_detector.py`
  - Asia range raids
  - Previous day high/low sweeps
  - Equal highs/lows raids
  - Session high/low sweeps
  - Quality scoring (clean sweep, wick, near miss)
  - Hold confirmation (time above/below level)

- [ ] `fvg_detector.py`
  - 15-minute Fair Value Gap detection
  - 3-candle pattern analysis
  - Gap size validation (minimum threshold)
  - Fill tracking

- [ ] `hourly_block_segmenter.py`
  - Divide each hour into 7 blocks (~8.57 min each)
  - Calculate block OHLC
  - Deviation from hour open
  - Bias direction (BULLISH/BEARISH/NEUTRAL)
  - Volatility score

- [ ] `market_structure_detector.py`
  - Break of Structure (BOS) detection
  - Change of Character (CHoCH) detection
  - Higher highs / Lower lows tracking
  - Displacement speed calculation (pips/minute)
  - Multi-timeframe support (15min, 1H, 4H)

#### Main Loop
- [ ] `agent1_main.py`
  - APScheduler integration (60-second interval)
  - Execution time tracking (<8s target)
  - Error handling with automatic retry
  - Graceful shutdown handling

#### Testing
- [ ] Unit tests for each calculator
- [ ] Integration test: fetch → calculate → store
- [ ] Mock yfinance responses for testing
- [ ] Validate against known data

**Success Criteria:**
- [ ] Fetches OHLC data every 60s with >95% success rate
- [ ] Execution time consistently <8 seconds
- [ ] All reference levels calculated correctly
- [ ] Fibonacci pivots match manual calculations
- [ ] Liquidity events detected with <10% false positives
- [ ] FVG detection accuracy >80%
- [ ] Data stored in Supabase without duplicates
- [ ] Runs continuously for 24 hours without crashes

**Dependencies:**
- Phase 1 (Database) ✅ Complete

**Estimated Effort:** 30-40 hours
**Timeline:** 5-7 days (solo dev), 3-4 days (pair dev)

**Files to Create:**
```
/agent1/
  ├── __init__.py
  ├── agent1_main.py                  # Entry point
  ├── config.py                        # Configuration
  ├── yahoo_finance_fetcher.py         # OHLC data fetcher
  ├── supabase_client.py               # DB connection
  ├── calculators/
  │   ├── __init__.py
  │   ├── reference_level_calculator.py
  │   ├── fibonacci_pivot_calculator.py
  │   ├── liquidity_event_detector.py
  │   ├── fvg_detector.py
  │   ├── hourly_block_segmenter.py
  │   └── market_structure_detector.py
  ├── utils/
  │   ├── __init__.py
  │   ├── timezone_manager.py          # ET/UTC conversion
  │   ├── market_hours_checker.py      # Holiday detection
  │   └── logger.py                    # Logging setup
  └── tests/
      ├── __init__.py
      ├── test_fetcher.py
      ├── test_reference_levels.py
      ├── test_fibonacci_pivots.py
      └── test_integration.py

requirements.txt
.env.example
README_AGENT1.md
```

**Risk Assessment:**
- **HIGH RISK:** yfinance API rate limits or downtime
  - Mitigation: Implement caching, retry logic, consider backup data source
- **MEDIUM RISK:** Timezone conversion errors (ET ↔ UTC)
  - Mitigation: Use `pytz` library, extensive testing
- **LOW RISK:** Calculation errors in Fibonacci pivots
  - Mitigation: Unit tests against manual calculations

---

### Phase 3: Agent 2 - Score Calculator 🎯 **HIGH PRIORITY**

**Status:** ❌ 0% Complete
**Duration:** Week 2-3 (7-10 days)
**Objective:** Build scoring engine that calculates dual-direction (bullish/bearish) scores from database data

**Priority:** **CRITICAL** - Core product functionality

**Deliverables:**

#### Core Infrastructure
- [ ] Project structure: `/agent2` directory
- [ ] Python virtual environment setup
- [ ] `requirements.txt` with dependencies
- [ ] Environment configuration
- [ ] Logging setup

#### Scoring Components (6 modules)

- [ ] `htf_bias_calculator.py` (30% weight)
  - Compare current price vs 8 reference levels
  - Distance decay factor (closer = higher score)
  - Weighted alignment calculation
  - Separate bullish/bearish scoring

- [ ] `kill_zone_calculator.py` (20% weight)
  - Session detection (London, NY AM/PM, Asian, Other)
  - Session position (first 25%, middle 50%, final 25%)
  - Time decay factor (0.70-1.00)
  - Day-of-week multiplier (Monday=1.0, Tuesday/Wednesday=1.15, Thursday=0.85, Friday=0.70)

- [ ] `pd_array_calculator.py` (25% weight)
  - Fibonacci pivot proximity (S1-S3, R1-R3)
  - Fair Value Gap (FVG) alignment
  - Previous Day/Week High/Low distance
  - Discount/Premium zone detection
  - Confluence multiplier (1.0x, 1.3x, 1.5x)

- [ ] `liquidity_calculator.py` (15% weight)
  - Recent raids (last 4 hours)
  - Raid quality scoring (clean sweep=1.0, wick=0.8, near miss=0.4)
  - Hold confirmation bonus (+0.20, +0.10, +0.05)
  - Raid weight by type (Asia=3.0, Prev Day H/L=2.5, etc.)

- [ ] `structure_calculator.py` (10% weight)
  - Break type (major=3.0, intermediate=2.0, minor=1.0)
  - Displacement quality (strong >20 pips in <15min = 1.0)
  - Separate bullish/bearish structure breaks

- [ ] `equilibrium_calculator.py` (±5% bonus/penalty)
  - Multi-timeframe alignment check
  - Price vs Daily/NY/4H/1H opens
  - Bonus for >70% agreement
  - Penalty for <30% agreement

#### Dual-Direction Engine
- [ ] `score_engine.py`
  - Calculate all 6 components for BOTH directions
  - Aggregate to 0-100 scores (with ±5 bonus)
  - Determine directional bias (BULLISH/BEARISH/NEUTRAL)
  - Calculate bias strength (Δ points)
  - Assign star rating (1-5 stars)

#### Block Prediction Module
- [ ] `block_prediction_engine.py`
  - 3 decision trees:
    1. Early Bias Validation (blocks 1-2)
    2. Counter-Trend Detection (blocks 3-5)
    3. Hour Close Prediction (after block 5)
  - Ensemble voting for confidence
  - Store predictions for validation

#### Triggers
- [ ] Auto-trigger: APScheduler cron (every 3 minutes)
- [ ] Manual trigger: API endpoint `/scores/calculate`

#### Main Loop
- [ ] `agent2_main.py`
  - APScheduler integration (3-minute cron: `*/3 * * * *`)
  - Execution time tracking (<3s target)
  - Store results to `score_history` table
  - Error handling with retry

#### Testing
- [ ] Unit tests for each component
- [ ] Integration test: full scoring pipeline
- [ ] Validate against manual calculations
- [ ] Backtest on historical data (7 days)

**Success Criteria:**
- [ ] Calculates scores every 3 minutes with >98% success rate
- [ ] Execution time consistently <3 seconds
- [ ] All 6 components calculate correctly
- [ ] Dual scores sum to expected totals
- [ ] Star ratings match score ranges
- [ ] Block predictions >70% accuracy (validated on 7 days)
- [ ] Scores stored in Supabase with full component breakdown
- [ ] Runs continuously for 7 days without crashes

**Dependencies:**
- Phase 1 (Database) ✅ Complete
- Phase 2 (Agent 1) ❌ Required

**Estimated Effort:** 40-50 hours
**Timeline:** 7-10 days (solo dev), 5-7 days (pair dev)

**Files to Create:**
```
/agent2/
  ├── __init__.py
  ├── agent2_main.py                   # Entry point
  ├── config.py                         # Configuration
  ├── supabase_client.py                # DB connection
  ├── components/
  │   ├── __init__.py
  │   ├── htf_bias_calculator.py
  │   ├── kill_zone_calculator.py
  │   ├── pd_array_calculator.py
  │   ├── liquidity_calculator.py
  │   ├── structure_calculator.py
  │   └── equilibrium_calculator.py
  ├── scoring/
  │   ├── __init__.py
  │   ├── score_engine.py               # Main dual-direction engine
  │   └── block_prediction_engine.py    # 3 decision trees
  ├── utils/
  │   ├── __init__.py
  │   └── logger.py
  └── tests/
      ├── __init__.py
      ├── test_htf_bias.py
      ├── test_kill_zone.py
      ├── test_pd_array.py
      ├── test_liquidity.py
      ├── test_structure.py
      ├── test_equilibrium.py
      ├── test_score_engine.py
      └── test_integration.py

requirements.txt
.env.example
README_AGENT2.md
```

**Risk Assessment:**
- **MEDIUM RISK:** Complex scoring logic with 6 components
  - Mitigation: Extensive unit tests, validate against manual calculations
- **MEDIUM RISK:** Decision tree accuracy for block predictions
  - Mitigation: Backtest on historical data, tune thresholds
- **LOW RISK:** Execution time >3 seconds
  - Mitigation: Optimize database queries, use connection pooling

---

### Phase 4: FastAPI Backend 🌐 **MEDIUM PRIORITY**

**Status:** ❌ 0% Complete
**Duration:** Week 3 (5-7 days)
**Objective:** Build REST API to expose scores and market data to frontend dashboard

**Deliverables:**

#### Core Setup
- [ ] FastAPI project structure
- [ ] Virtual environment
- [ ] `requirements.txt`:
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  supabase>=2.0.0
  pydantic>=2.5.0
  slowapi>=0.1.9  # Rate limiting
  python-dotenv>=1.0.0
  ```

#### API Routes (18 endpoints)

**Score Endpoints** (5)
- [ ] `GET /scores/latest` - Get latest dual scores for instrument
- [ ] `GET /scores/history` - Historical scores with pagination
- [ ] `POST /scores/calculate` - Manual trigger for Agent 2
- [ ] `GET /scores/{id}` - Get specific score by ID
- [ ] `GET /scores/stats` - Score statistics (avg, min, max)

**Market Data Endpoints** (6)
- [ ] `GET /market/price` - Current price
- [ ] `GET /market/levels` - Reference levels (opens)
- [ ] `GET /market/pivots` - Fibonacci pivots
- [ ] `GET /market/liquidity` - Recent liquidity events
- [ ] `GET /market/structure` - Market structure breaks
- [ ] `GET /market/fvg` - Fair Value Gaps

**Block Endpoints** (3)
- [ ] `GET /blocks/current` - Current hourly block
- [ ] `GET /blocks/history` - Historical blocks
- [ ] `GET /blocks/predictions` - Block predictions

**System Endpoints** (4)
- [ ] `GET /health` - Service health check
- [ ] `GET /status` - Agent 1 & Agent 2 status
- [ ] `GET /instruments` - Available instruments
- [ ] `GET /openapi.json` - OpenAPI spec

#### Middleware & Security
- [ ] CORS middleware (allow dashboard origin)
- [ ] Rate limiting (slowapi):
  - Score generation: 6/min
  - Score retrieval: 60/min
  - Market data: 120/min
- [ ] Request validation (Pydantic models)
- [ ] Error handling (standardized responses)
- [ ] Request logging

#### Service Layer
- [ ] `score_service.py` - Business logic for scores
- [ ] `market_data_service.py` - Market data queries
- [ ] `supabase_repository.py` - Database access

#### Testing
- [ ] Unit tests for services
- [ ] Integration tests for endpoints
- [ ] Load test with 1000 concurrent requests

**Success Criteria:**
- [ ] All 18 endpoints functional
- [ ] Response time <200ms for GET requests
- [ ] Rate limiting works correctly
- [ ] CORS configured for dashboard
- [ ] OpenAPI spec generated
- [ ] Error responses standardized
- [ ] Handles 100 concurrent requests

**Dependencies:**
- Phase 1 (Database) ✅ Complete
- Phase 2 (Agent 1) ❌ Required (for data)
- Phase 3 (Agent 2) ❌ Required (for scores)

**Estimated Effort:** 25-30 hours
**Timeline:** 5-7 days

**Files to Create:**
```
/backend/
  ├── __init__.py
  ├── main.py                          # FastAPI app
  ├── config.py                         # Configuration
  ├── routes/
  │   ├── __init__.py
  │   ├── scores.py                    # Score endpoints
  │   ├── market.py                    # Market data endpoints
  │   ├── blocks.py                    # Block endpoints
  │   └── system.py                    # System endpoints
  ├── services/
  │   ├── __init__.py
  │   ├── score_service.py
  │   ├── market_data_service.py
  │   └── supabase_repository.py
  ├── models/
  │   ├── __init__.py
  │   ├── score_models.py              # Pydantic models
  │   └── market_models.py
  ├── middleware/
  │   ├── __init__.py
  │   ├── cors.py
  │   ├── rate_limiter.py
  │   └── error_handler.py
  └── tests/
      ├── __init__.py
      ├── test_scores_endpoints.py
      ├── test_market_endpoints.py
      └── test_integration.py

requirements.txt
.env.example
README_BACKEND.md
```

---

### Phase 5: React Dashboard 📱 **HIGH PRIORITY**

**Status:** ❌ 0% Complete
**Duration:** Week 4 (7-10 days)
**Objective:** Build responsive web dashboard to display dual scores in real-time

**Deliverables:**

#### Project Setup
- [ ] Create React app with TypeScript
- [ ] Bootstrap 5 for styling
- [ ] Supabase client for real-time subscriptions
- [ ] `package.json` dependencies:
  ```json
  {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "bootstrap": "^5.3.0",
    "@supabase/supabase-js": "^2.38.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  }
  ```

#### Core Components (11)

**Layout Components**
- [ ] `Header.tsx` - Top navigation with instrument selector
- [ ] `LeftPanel.tsx` - Reference levels, session info (desktop only)
- [ ] `RightPanel.tsx` - Charts, liquidity events (desktop only)
- [ ] `Footer.tsx` - Status info

**Score Display Components**
- [ ] `DualScoreDisplay.tsx` - Side-by-side bullish/bearish cards
- [ ] `ScoreCard.tsx` - Individual score card (72px number, stars, rating)
- [ ] `DirectionalBias.tsx` - Bias badge with strength indicator

**Breakdown Components**
- [ ] `ComponentBreakdown.tsx` - 6 component cards per direction
- [ ] `ComponentCard.tsx` - Single component (HTF, Kill Zone, etc.)

**Action Components**
- [ ] `ActionButtons.tsx` - Generate score, view history
- [ ] `AutoRefreshTimer.tsx` - Countdown timer (3:00 → 0:00)

#### Real-Time Integration
- [ ] Supabase subscription to `score_history` table
- [ ] Live updates on new score inserts
- [ ] Connection status indicator
- [ ] Automatic reconnection on disconnect

#### Responsive Design
- [ ] Desktop (1200px+): 3-column layout
- [ ] Tablet (768-1199px): 2-column layout
- [ ] Mobile (<768px): Single-column stacked

#### State Management
- [ ] Context API for scores
- [ ] Custom hooks:
  - `useScore()` - Current score & refresh
  - `useHistoricalScores()` - Historical data
  - `useMarketData()` - Reference levels, pivots

#### Features
- [ ] Manual score generation button
- [ ] Auto-refresh timer (3-minute countdown)
- [ ] Historical scores modal with filters
- [ ] Dark mode toggle
- [ ] Instrument selector (NQ=F, ES=F, etc.)

**Success Criteria:**
- [ ] Real-time updates appear within 3 seconds
- [ ] Manual refresh works
- [ ] All components responsive (mobile/tablet/desktop)
- [ ] Bundle size <1MB
- [ ] Initial load <2 seconds
- [ ] Accessible (keyboard navigation, ARIA labels)

**Dependencies:**
- Phase 1 (Database) ✅ Complete
- Phase 4 (Backend) ❌ Optional (can use Supabase directly)

**Estimated Effort:** 35-45 hours
**Timeline:** 7-10 days

**Files to Create:**
```
/frontend/
  ├── public/
  │   └── index.html
  ├── src/
  │   ├── index.tsx                    # Entry point
  │   ├── App.tsx                      # Main app component
  │   ├── context/
  │   │   └── ScoreContext.tsx         # Global state
  │   ├── hooks/
  │   │   ├── useScore.ts
  │   │   ├── useHistoricalScores.ts
  │   │   └── useMarketData.ts
  │   ├── components/
  │   │   ├── layout/
  │   │   │   ├── Header.tsx
  │   │   │   ├── LeftPanel.tsx
  │   │   │   ├── RightPanel.tsx
  │   │   │   └── Footer.tsx
  │   │   ├── scores/
  │   │   │   ├── DualScoreDisplay.tsx
  │   │   │   ├── ScoreCard.tsx
  │   │   │   └── DirectionalBias.tsx
  │   │   ├── breakdown/
  │   │   │   ├── ComponentBreakdown.tsx
  │   │   │   └── ComponentCard.tsx
  │   │   └── actions/
  │   │       ├── ActionButtons.tsx
  │   │       └── AutoRefreshTimer.tsx
  │   ├── styles/
  │   │   ├── _variables.scss
  │   │   ├── _dashboard.scss
  │   │   └── index.scss
  │   ├── utils/
  │   │   ├── supabaseClient.ts
  │   │   └── formatters.ts
  │   └── types/
  │       └── score.types.ts
  ├── package.json
  ├── tsconfig.json
  └── README_FRONTEND.md
```

---

### Phase 6: Testing & Validation 🧪 **CRITICAL**

**Status:** ❌ 0% Complete
**Duration:** Week 4-5 (3-5 days, parallel with Phase 5)
**Objective:** Ensure system reliability through comprehensive testing

**Deliverables:**

#### Unit Tests
- [ ] Agent 1: Test each calculator independently
- [ ] Agent 2: Test each scoring component independently
- [ ] Backend: Test each service function

#### Integration Tests
- [ ] Agent 1 → Supabase pipeline
- [ ] Agent 2 → Supabase pipeline
- [ ] Backend → Supabase queries
- [ ] Frontend → Backend API

#### End-to-End Tests
- [ ] Full data flow: yfinance → Agent 1 → Supabase → Agent 2 → API → Dashboard
- [ ] Real-time subscription flow
- [ ] Manual refresh flow

#### Backtesting
- [ ] Run Agent 2 on 7 days of historical data
- [ ] Validate block predictions (>70% accuracy target)
- [ ] Compare scores against manual calculations

#### Performance Tests
- [ ] Agent 1 execution time (<8s)
- [ ] Agent 2 execution time (<3s)
- [ ] API response time (<200ms)
- [ ] Database query performance
- [ ] Frontend load time (<2s)

#### Load Tests
- [ ] 100 concurrent API requests
- [ ] 1000 concurrent API requests
- [ ] Real-time subscriptions with 50 clients

**Success Criteria:**
- [ ] >95% test coverage for critical paths
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Backtesting shows >70% prediction accuracy
- [ ] Performance targets met
- [ ] No crashes under load

**Dependencies:**
- All previous phases (1-5)

**Estimated Effort:** 20-25 hours
**Timeline:** 3-5 days (can run in parallel with Phase 5)

---

### Phase 7: Deployment 🚀 **HIGH PRIORITY**

**Status:** ❌ 0% Complete
**Duration:** Week 5 (3-5 days)
**Objective:** Deploy to production environment

**Deliverables:**

#### Supabase Production
- [ ] Production Supabase project created
- [ ] Run migrations (001-007)
- [ ] Configure environment variables
- [ ] Enable real-time subscriptions
- [ ] Set up database backups

#### Backend Deployment (Render.com)
- [ ] Create 3 services:
  1. **API Service** (FastAPI web service)
  2. **Agent 1 Service** (background worker)
  3. **Agent 2 Service** (background worker)
- [ ] Configure environment variables
- [ ] Set up health checks (`/health` endpoint)
- [ ] Configure auto-restart on failure

#### Frontend Deployment
- [ ] Deploy to Vercel or Netlify
- [ ] Configure environment variables (API URL, Supabase keys)
- [ ] Set up custom domain (optional)
- [ ] Configure CORS for production

#### Monitoring
- [ ] Health check monitoring (every 30s)
- [ ] Email alerts for service downtime
- [ ] Log aggregation (Render.com logs)
- [ ] Error tracking (Sentry, optional)

**Success Criteria:**
- [ ] All services deployed and running
- [ ] Health checks passing
- [ ] Dashboard accessible via public URL
- [ ] Real-time updates working in production
- [ ] 24-hour uptime test passing

**Dependencies:**
- Phases 1-5 complete

**Estimated Effort:** 15-20 hours
**Timeline:** 3-5 days

---

### Phase 8: Documentation & Handoff 📚 **MEDIUM PRIORITY**

**Status:** ❌ 0% Complete
**Duration:** Week 5 (2-3 days, parallel with Phase 7)
**Objective:** Document system for maintenance and future development

**Deliverables:**

#### Technical Documentation
- [ ] `API_DOCUMENTATION.md` - All endpoints with examples
- [ ] `ARCHITECTURE.md` - System architecture diagram
- [ ] `DATABASE_SCHEMA.md` - Table relationships and queries
- [ ] `DEPLOYMENT_GUIDE.md` - Step-by-step deployment

#### Operational Documentation
- [ ] `OPERATIONS_RUNBOOK.md` - Monitoring, troubleshooting, incident response
- [ ] `MAINTENANCE_GUIDE.md` - Regular tasks, backups, updates
- [ ] `TROUBLESHOOTING.md` - Common issues and solutions

#### User Documentation
- [ ] `USER_GUIDE.md` - How to use the dashboard
- [ ] `FAQ.md` - Frequently asked questions
- [ ] Video walkthrough (optional)

#### Code Documentation
- [ ] Docstrings for all functions
- [ ] README for each module (Agent 1, Agent 2, Backend, Frontend)
- [ ] Code comments for complex logic

**Success Criteria:**
- [ ] All documentation complete
- [ ] Documentation reviewed by stakeholder
- [ ] Knowledge transfer session completed

**Dependencies:**
- Phases 1-7 (documentation happens throughout)

**Estimated Effort:** 10-15 hours
**Timeline:** 2-3 days

---

## 📅 Gantt Chart Timeline

**Total Duration:** 5-6 weeks (solo dev), 3-4 weeks (pair dev)

```
Week 1:
├─ Phase 1: Database ✅ (DONE)
└─ Phase 2: Agent 1 🚧 (START)

Week 2:
├─ Phase 2: Agent 1 (FINISH)
└─ Phase 3: Agent 2 🚧 (START)

Week 3:
├─ Phase 3: Agent 2 (FINISH)
├─ Phase 4: Backend 🚧 (START)
└─ Phase 6: Testing 🧪 (START - parallel)

Week 4:
├─ Phase 4: Backend (FINISH)
├─ Phase 5: Frontend 🚧 (START)
└─ Phase 6: Testing (CONTINUE)

Week 5:
├─ Phase 5: Frontend (FINISH)
├─ Phase 6: Testing (FINISH)
├─ Phase 7: Deployment 🚀 (START & FINISH)
└─ Phase 8: Documentation 📚 (START & FINISH)

Week 6: (Buffer)
└─ Bug fixes, polish, final testing
```

---

## 🎯 Priority Matrix

### Immediate (Week 1-2)
1. **Agent 1 Data Collector** - CRITICAL
   - Blocks all downstream work
   - Start immediately

### Short-term (Week 2-3)
2. **Agent 2 Score Calculator** - CRITICAL
   - Core product value
   - High complexity

3. **Backend API** - HIGH
   - Required for dashboard
   - Can start in parallel with Agent 2 testing

### Medium-term (Week 3-4)
4. **React Dashboard** - HIGH
   - User-facing component
   - Can use Supabase directly if backend delayed

5. **Testing** - CRITICAL
   - Run in parallel with development
   - Essential for reliability

### Final (Week 5)
6. **Deployment** - HIGH
   - Final integration
   - Production readiness

7. **Documentation** - MEDIUM
   - Ongoing throughout
   - Final polish at end

---

## ⚠️ Risk Assessment

### High Risks

**Risk:** yfinance API rate limits or downtime
**Impact:** Agent 1 cannot fetch data → entire system blocked
**Mitigation:**
- Implement aggressive caching (50s TTL)
- Add retry logic (3 attempts, exponential backoff)
- Consider backup data source (Alpha Vantage, IEX Cloud)
- Monitor API status and switch providers if needed

**Risk:** Complex scoring logic errors in Agent 2
**Impact:** Incorrect scores → loss of user trust
**Mitigation:**
- Extensive unit tests for each component
- Validate against manual calculations
- Backtest on historical data (7 days minimum)
- Add logging for all component calculations

**Risk:** Real-time subscriptions not working in production
**Impact:** Dashboard doesn't update → poor UX
**Mitigation:**
- Test Supabase real-time in production environment early
- Implement fallback polling (every 30s) if subscriptions fail
- Add connection status indicator in UI

### Medium Risks

**Risk:** Performance targets not met (API >200ms, Agent 1 >8s, Agent 2 >3s)
**Impact:** Slow user experience, high server costs
**Mitigation:**
- Profile code early and often
- Optimize database queries (indexes, materialized views)
- Use connection pooling
- Consider Redis caching for frequently accessed data

**Risk:** Timezone conversion errors (ET ↔ UTC)
**Impact:** Incorrect reference levels → wrong scores
**Mitigation:**
- Use `pytz` library for conversions
- Extensive testing across timezone boundaries
- Log all timezone conversions for debugging

**Risk:** Deployment complexity with 3 services (API + Agent 1 + Agent 2)
**Impact:** Deployment delays, configuration errors
**Mitigation:**
- Use environment variable templates
- Document deployment steps clearly
- Test deployment in staging environment first
- Use health checks to verify services

### Low Risks

**Risk:** Frontend bundle size >1MB
**Impact:** Slow initial load
**Mitigation:**
- Code splitting
- Lazy loading for charts and modals
- Tree shaking unused libraries

**Risk:** Dark mode not working correctly
**Impact:** Poor UX for some users
**Mitigation:**
- Test dark mode early
- Use CSS variables for theming
- Fallback to light mode if issues

---

## 📊 Success Metrics

### MVP Success Criteria (End of Week 5)

**System Reliability**
- [ ] Agent 1: >95% fetch success rate
- [ ] Agent 2: >98% calculation success rate
- [ ] API: >99% uptime during market hours
- [ ] Dashboard: <1 hour downtime per week

**Performance**
- [ ] Agent 1: <8s execution time (95th percentile)
- [ ] Agent 2: <3s execution time (95th percentile)
- [ ] API: <200ms response for `/scores/latest`
- [ ] Dashboard: <2s initial load, <500ms real-time updates

**Accuracy**
- [ ] Block predictions: >70% accuracy (7-day backtest)
- [ ] Reference levels: 100% match manual calculations
- [ ] Fibonacci pivots: 100% match manual calculations
- [ ] Liquidity detection: <10% false positives

**Data Management**
- [ ] Database size: <10MB/month compressed
- [ ] 30-day retention working (auto-cleanup)
- [ ] 7-day compression working (60% savings)
- [ ] No duplicate records in OHLC data

**User Experience**
- [ ] Real-time updates working
- [ ] Manual refresh working
- [ ] Responsive on mobile/tablet/desktop
- [ ] Accessible (keyboard navigation, ARIA)

### Production Success Criteria (End of Week 6)

**User Adoption**
- [ ] 10+ active users testing dashboard
- [ ] Positive feedback on score accuracy
- [ ] <5 bug reports per week

**System Stability**
- [ ] 7-day continuous uptime test passing
- [ ] Zero crashes or fatal errors
- [ ] All error logs reviewed and addressed

**Documentation**
- [ ] All documentation complete
- [ ] Knowledge transfer to stakeholder
- [ ] Operational runbook tested in real scenario

---

## 🔄 Iteration Strategy

### Sprint 1 (Week 1-2): Data Foundation
**Goal:** Get data flowing into database
- Phase 1 ✅ (Done)
- Phase 2 (Agent 1)
- **Demo:** Show live OHLC data, reference levels, pivots in database

### Sprint 2 (Week 2-3): Scoring Engine
**Goal:** Generate first scores
- Phase 3 (Agent 2)
- **Demo:** Show dual scores being generated every 3 minutes

### Sprint 3 (Week 3-4): API & Dashboard
**Goal:** Make scores visible to users
- Phase 4 (Backend API)
- Phase 5 (React Dashboard)
- **Demo:** Show live dashboard with real-time updates

### Sprint 4 (Week 4-5): Testing & Deployment
**Goal:** Production-ready system
- Phase 6 (Testing)
- Phase 7 (Deployment)
- Phase 8 (Documentation)
- **Demo:** Show production dashboard with 24-hour uptime

---

## 🛠️ Development Guidelines

### Workability First Principles

1. **Start Simple, Add Complexity Later**
   - MVP features only (dual scores, basic UI)
   - Skip: Advanced filtering, export, sharing, user accounts

2. **Hardcode Where Needed**
   - Single instrument (NQ=F) initially
   - Add multi-instrument support later
   - Hardcode API keys in `.env` (move to secrets manager later)

3. **Use Existing Tools**
   - Bootstrap 5 (no custom CSS framework)
   - Chart.js (no custom charting)
   - Supabase client (no custom database layer)

4. **Defer Optimization**
   - Get it working first
   - Optimize only if performance targets missed
   - Profile before optimizing

5. **Minimal Error Handling Initially**
   - Basic try/catch blocks
   - Log errors, don't crash
   - Improve error handling in Phase 6

### Code Quality Standards

**Python (Agents & Backend)**
- Use type hints (PEP 484)
- Docstrings for all functions
- Follow PEP 8 style guide
- Use `black` for formatting (optional)

**TypeScript (Frontend)**
- Strict mode enabled
- Props interfaces for all components
- ESLint for linting (optional)

**Testing**
- Unit tests for critical functions
- Integration tests for data pipelines
- Manual testing for UI

---

## 📦 Deliverables Summary

### Phase 1 ✅ (Complete)
- [x] Database migrations (7 files)
- [x] Database README
- [x] Common queries

### Phase 2 (Agent 1)
- [ ] `/agent1` directory with 15+ files
- [ ] 6 calculator modules
- [ ] 60-second fetch loop
- [ ] Unit tests

### Phase 3 (Agent 2)
- [ ] `/agent2` directory with 12+ files
- [ ] 6 scoring components
- [ ] Dual-direction engine
- [ ] 3-minute trigger loop
- [ ] Unit tests

### Phase 4 (Backend)
- [ ] `/backend` directory with 15+ files
- [ ] 18 API endpoints
- [ ] OpenAPI spec
- [ ] Integration tests

### Phase 5 (Frontend)
- [ ] `/frontend` directory with 20+ files
- [ ] 11 React components
- [ ] Real-time subscriptions
- [ ] Responsive UI

### Phase 6 (Testing)
- [ ] Test suites for all modules
- [ ] Backtest results (7 days)
- [ ] Performance test results
- [ ] Load test results

### Phase 7 (Deployment)
- [ ] Production Supabase
- [ ] 3 Render.com services
- [ ] Frontend deployment (Vercel/Netlify)
- [ ] Monitoring setup

### Phase 8 (Documentation)
- [ ] API documentation
- [ ] Architecture diagram
- [ ] Operations runbook
- [ ] User guide

---

## 🚦 Go/No-Go Decision Points

### After Phase 2 (Agent 1)
**Go Criteria:**
- Agent 1 runs for 24 hours without crashes
- OHLC data fetched with >90% success rate
- Reference levels match manual calculations
- Fibonacci pivots match manual calculations

**No-Go Risks:**
- yfinance API unreliable (<80% success)
- Execution time >10 seconds consistently
- Major calculation errors

**Decision:** Proceed to Phase 3 OR switch data provider

### After Phase 3 (Agent 2)
**Go Criteria:**
- Agent 2 runs for 24 hours without crashes
- Scores generated every 3 minutes
- All 6 components calculate correctly
- Backtest shows >60% prediction accuracy (acceptable)

**No-Go Risks:**
- Execution time >5 seconds consistently
- Scores don't match manual calculations
- Backtest shows <50% prediction accuracy

**Decision:** Proceed to Phase 4 OR revise scoring weights

### After Phase 5 (Dashboard)
**Go Criteria:**
- Dashboard loads in <3 seconds
- Real-time updates working
- Responsive on mobile/tablet/desktop
- Manual refresh working

**No-Go Risks:**
- Real-time subscriptions not working
- Performance <60 FPS
- Major UI bugs

**Decision:** Proceed to deployment OR fix critical issues

---

## 📞 Stakeholder Communication Plan

### Weekly Updates
- **Every Monday:** Progress report (phases completed, blockers)
- **Every Friday:** Demo of working features

### Milestone Demos
- **End of Week 2:** Agent 1 + Agent 2 working (show scores in database)
- **End of Week 4:** Dashboard working (show live UI)
- **End of Week 5:** Production deployment (show public URL)

### Decision Points
- **Week 2:** Data provider selection (yfinance vs alternatives)
- **Week 3:** Deployment platform selection (Render vs Heroku vs Railway)
- **Week 4:** Feature freeze decision (what goes in MVP vs future)

---

## 🎓 Learning & Improvement

### Post-MVP Retrospective (Week 6)
- What went well?
- What could be improved?
- What surprised us?
- What should we change for next iteration?

### Metrics to Track
- Actual time vs estimated time (per phase)
- Bug count per phase
- Code churn (lines added/deleted)
- Deployment attempts (success vs failure)

### Future Enhancements (Post-MVP)
- Multi-instrument support (ES=F, GC, CL)
- User accounts and preferences
- Historical score export (CSV, JSON)
- Advanced filtering (component-specific, date range)
- Mobile app (React Native)
- Webhook notifications (Discord, Telegram)
- Backtesting tool (test scoring on historical data)
- Machine learning for prediction improvement

---

## ✅ Next Actions (Immediate)

### This Week
1. **Set up development environment**
   - Install Python 3.11+
   - Install Node.js 18+
   - Set up virtual environments

2. **Create project structure**
   ```bash
   mkdir -p agent1 agent2 backend frontend
   ```

3. **Start Agent 1 development**
   - Create `requirements.txt`
   - Set up `.env` with Supabase credentials
   - Implement `yahoo_finance_fetcher.py`
   - Test OHLC fetch (manual run)

4. **Run database migrations**
   - Ensure Supabase project exists
   - Run migrations 001-007
   - Verify tables created

5. **Track progress**
   - Update this roadmap weekly
   - Log blockers and decisions
   - Celebrate milestones!

---

## 📝 Document Control

**Version:** 1.0
**Created:** November 16, 2025
**Author:** Development Team
**Review Frequency:** Weekly
**Next Review:** November 23, 2025

**Change Log:**
- v1.0 (Nov 16, 2025): Initial roadmap created based on project analysis

---

**End of Product Roadmap**

For questions or updates, reference this document and update as the project evolves. 🚀
