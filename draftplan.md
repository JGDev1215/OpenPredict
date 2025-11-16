ICT Quantitative Prediction Model - Master Implementation Plan                                    │
     │                                                                                                   │
     │ Phase 1: Database Setup (Week 1)                                                                  │
     │                                                                                                   │
     │ - Create Supabase project and enable TimescaleDB extension                                        │
     │ - Deploy complete database schema (10 tables with indexes)                                        │
     │ - Set up row-level security policies                                                              │
     │ - Configure real-time subscriptions for score_history table                                       │
     │ - Create materialized views for reference levels                                                  │
     │ - Test database connections and query performance                                                 │
     │                                                                                                   │
     │ Phase 2: Agent 1 - Data Collector (Week 1-2)                                                      │
     │                                                                                                   │
     │ - Implement yfinance fetcher with exponential backoff retry (3 attempts)                          │
     │ - Build reference level calculator (8 levels: weekly/daily/NY opens, etc.)                        │
     │ - Create Fibonacci pivot calculator (weekly & daily S3-R3)                                        │
     │ - Develop liquidity event detector (raids, sweeps with quality scoring)                           │
     │ - Implement FVG detector (15-min timeframe, 3-candle pattern)                                     │
     │ - Build hourly block segmenter (7 blocks per hour)                                                │
     │ - Integrate APScheduler with 60-second interval trigger                                           │
     │ - Test Agent 1 end-to-end with error handling                                                     │
     │                                                                                                   │
     │ Phase 3: Agent 2 - Score Calculator (Week 2)                                                      │
     │                                                                                                   │
     │ - Implement HTF Bias component (30% weight, 8 reference levels)                                   │
     │ - Build Kill Zone component (20% weight, session timing + day multipliers)                        │
     │ - Create PD Array component (25% weight, confluence multipliers)                                  │
     │ - Develop Liquidity component (15% weight, raid quality + hold bonus)                             │
     │ - Implement Structure component (10% weight, break types + displacement)                          │
     │ - Build Equilibrium component (±5% bonus/penalty, multi-TF alignment)                             │
     │ - Integrate 3 decision trees for block predictions                                                │
     │ - Add dual-trigger support (auto 3-min cron + manual API)                                         │
     │ - Test scoring accuracy with sample data                                                          │
     │                                                                                                   │
     │ Phase 4: FastAPI Backend (Week 3)                                                                 │
     │                                                                                                   │
     │ - Set up FastAPI project structure (5 route modules)                                              │
     │ - Implement 18 REST endpoints with Pydantic validation                                            │
     │ - Add CORS middleware with security headers                                                       │
     │ - Implement rate limiting (slowapi: 6/min for generation, 60/min for retrieval)                   │
     │ - Create custom exception handlers with standardized error responses                              │
     │ - Build service layer for business logic (score_service, market_data_service, etc.)               │
     │ - Add pagination support for historical queries                                                   │
     │ - Generate OpenAPI 3.0 spec and test Swagger UI                                                   │
     │ - Deploy to Render.com with 3 services (API + Agent1 + Agent2)                                    │
     │                                                                                                   │
     │ Phase 5: React Dashboard (Week 3-4)                                                               │
     │                                                                                                   │
     │ - Set up React project with TypeScript + Bootstrap 5                                              │
     │ - Implement minimal/clean design system (3-color palette, 2 font weights)                         │
     │ - Build dual score display component (side-by-side bullish/bearish)                               │
     │ - Create hourly block timeline component (7 blocks, swipeable on mobile)                          │
     │ - Add block prediction panel with confidence meter                                                │
     │ - Implement component breakdown accordion (collapsible)                                           │
     │ - Set up Supabase real-time subscriptions (score updates every 3 min)                             │
     │ - Build "Generate Score" manual trigger button                                                    │
     │ - Add responsive mobile layout (single-column, sticky header)                                     │
     │ - Optimize performance (bundle <1MB, initial load <2s)                                            │
     │                                                                                                   │
     │ Phase 6: Testing & Validation (Week 4)                                                            │
     │                                                                                                   │
     │ - Write unit tests for all 6 scoring components (pytest)                                          │
     │ - Create integration tests for Agent 1 → Supabase pipeline                                        │
     │ - Test Agent 2 score calculation end-to-end                                                       │
     │ - Validate API endpoints (200 OK, 404, 422, 429, 503 responses)                                   │
     │ - Backtest scoring model on 7 days of historical data                                             │
     │ - Measure performance metrics (Agent1 <8s, Agent2 <3s, API <200ms)                                │
     │ - Test real-time Supabase subscriptions                                                           │
     │ - Verify data retention policies (auto-cleanup after 30 days)                                     │
     │ - Load test with 1000 concurrent API requests                                                     │
     │                                                                                                   │
     │ Phase 7: Production Deployment (Week 5)                                                           │
     │                                                                                                   │
     │ - Deploy Supabase database to production                                                          │
     │ - Configure environment variables on Render.com (SUPABASE_URL, SUPABASE_KEY)                      │
     │ - Deploy API service to Render.com Web Service                                                    │
     │ - Deploy Agent 1 as background worker                                                             │
     │ - Deploy Agent 2 as background worker                                                             │
     │ - Set up health check monitoring (/health endpoint every 30s)                                     │
     │ - Configure Render.com email alerts for service downtime                                          │
     │ - Deploy React frontend (Vercel/Netlify recommended)                                              │
     │ - Test production endpoints and real-time updates                                                 │
     │ - Monitor logs for 24 hours to verify stability                                                   │
     │                                                                                                   │
     │ Phase 8: Documentation & Handoff (Week 5)                                                         │
     │                                                                                                   │
     │ - Create implementationguide.md with all architectural decisions                                  │
     │ - Document API endpoints with request/response examples                                           │
     │ - Write operational runbook (deployment, monitoring, troubleshooting)                             │
     │ - Create user guide for dashboard UI                                                              │
     │ - Generate OpenAPI spec and publish to public docs                                                │
     │ - Set up Sentry/Datadog for error tracking (optional)                                             │
     │ - Train team on system architecture and maintenance procedures                                    │
     │                                                                                                   │
     │ Success Criteria                                                                                  │
     │                                                                                                   │
     │ ✅ Agent 1 fetches OHLC data every 60s with >95% success rate                                     │
     │ ✅ Agent 2 calculates scores every 3 min with >98% success rate                                   │
     │ ✅ API responds to /scores/latest in <200ms                                                       │
     │ ✅ Dashboard updates in real-time via Supabase subscriptions                                      │
     │ ✅ Hourly block predictions achieve >70% accuracy (validated on 7 days)                           │
     │ ✅ System runs continuously for 7 days with <1 hour downtime                                      │
     │ ✅ Database stores 30 days of data with auto-cleanup                                              │
     │                                                                                                   │
     │ Total Timeline: 5 weeks                                                                           │
     │                                                                                                   │
     │ - Week 1: Database + Agent 1 foundation                                                           │
     │ - Week 2: Agent 2 scoring logic + initial testing                                                 │
     │ - Week 3: FastAPI backend + Render.com deployment                                                 │
     │ - Week 4: React dashboard + comprehensive testing                                                 │
     │ - Week 5: Production deployment + monitoring + documentation                                      │
     │                                                                                                   │
     │ After completion, the system will generate bullish/bearish scores every 3 minutes, update the     │
     │ dashboard in real-time, and provide hourly block predictions with full audit trails and           │
     │ historical validation.  