# Agent 1 - Data Collector: Testing & Deployment Guide

Complete testing and deployment infrastructure for Phase 2 Agent 1 - Data Collector.

## Quick Start

### 1. Read the Executive Summary (Start Here)
```bash
open TESTING_AND_DEPLOYMENT_SUMMARY.md
```
Provides: Overview, timeline, metrics, quick commands

### 2. Run Pre-Deployment Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Health check
python deployment/health_check.py --all

# Run all tests
pytest tests/ -v --cov=. --cov-report=html

# Performance benchmark
python monitoring/performance_benchmark.py --cycles 100
```

### 3. Follow Deployment Guide
```bash
# Step-by-step instructions
open deployment/QUICK_START_GUIDE.md

# Or comprehensive technical guide
open deployment/TESTING_DEPLOYMENT_STRATEGY.md
```

## Documentation Structure

```
agent1/
├── TESTING_AND_DEPLOYMENT_SUMMARY.md  ← START HERE (Executive Summary)
├── TESTING_FILES_OVERVIEW.md          ← File structure and overview
├── README_TESTING_DEPLOYMENT.md       ← This file
│
├── deployment/                         ← Deployment resources
│   ├── TESTING_DEPLOYMENT_STRATEGY.md ← Complete 72-page technical guide
│   ├── QUICK_START_GUIDE.md           ← Step-by-step walkthrough
│   ├── DEPLOYMENT_CHECKLIST.md        ← Production checklist
│   ├── health_check.py                ← System health validation
│   ├── agent1-staging.service         ← Staging systemd service
│   └── agent1-production.service      ← Production systemd service
│
├── monitoring/                         ← Monitoring & validation tools
│   ├── continuous_monitor.py          ← 24-hour test monitoring
│   ├── performance_benchmark.py       ← Performance benchmarking
│   └── data_quality_validator.py      ← Data integrity validation
│
├── tests/                              ← Test suites
│   ├── test_reference_levels.py       ← Unit tests
│   ├── test_fibonacci_pivots.py       ← Unit tests
│   ├── test_integration.py            ← Integration tests
│   └── edge_cases/
│       └── test_edge_cases.py         ← 20+ edge case tests
│
├── pytest.ini                          ← Pytest configuration
└── requirements-test.txt               ← Test dependencies
```

## Key Resources

### Documentation (4 Files)

| File | Purpose | Size |
|------|---------|------|
| `TESTING_AND_DEPLOYMENT_SUMMARY.md` | Executive summary | 650 lines |
| `deployment/TESTING_DEPLOYMENT_STRATEGY.md` | Complete technical guide | 1,450 lines |
| `deployment/QUICK_START_GUIDE.md` | Step-by-step walkthrough | 700 lines |
| `deployment/DEPLOYMENT_CHECKLIST.md` | Production checklist | 300 lines |

### Scripts (4 Executable Tools)

| Script | Purpose | Usage |
|--------|---------|-------|
| `deployment/health_check.py` | System health validation | `python deployment/health_check.py --all` |
| `monitoring/continuous_monitor.py` | 24-hour test monitoring | `python monitoring/continuous_monitor.py --duration 24` |
| `monitoring/performance_benchmark.py` | Performance benchmarking | `python monitoring/performance_benchmark.py --cycles 100` |
| `monitoring/data_quality_validator.py` | Data quality validation | `python monitoring/data_quality_validator.py --window 1` |

### Tests (4 Test Files)

| Test File | Purpose | Test Count |
|-----------|---------|------------|
| `tests/test_reference_levels.py` | Reference levels unit tests | 3 tests |
| `tests/test_fibonacci_pivots.py` | Fibonacci pivots unit tests | 4 tests |
| `tests/test_integration.py` | Integration tests | 2 tests |
| `tests/edge_cases/test_edge_cases.py` | Edge case tests | 20+ tests |

## Target Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Success Rate | >95% | 90-95% | <90% |
| Execution Time (P95) | <8s | 8-10s | >10s |
| Test Coverage | >98% | 95-98% | <95% |
| Memory Usage | <500 MB | 500-750 MB | >750 MB |
| Service Uptime | >99% | 95-99% | <95% |

## Deployment Phases

### Phase 1: Pre-Deployment Testing
- Install dependencies
- Run health checks
- Execute unit tests (98%+ coverage)
- Run edge case tests (20+ scenarios)
- Performance benchmark (<8s execution time)

**Duration:** 1-2 days

### Phase 2: Staging Deployment
- Setup staging environment
- Install systemd service
- Validate deployment
- Monitor stability

**Duration:** 2-3 days

### Phase 3: 24-Hour Continuous Test
- Start monitoring
- Run continuous test (1,440 cycles)
- Validate data quality
- Test error recovery
- Analyze results

**Duration:** 2 days (test + analysis)

### Phase 4: Production Deployment
- Pre-deployment verification
- Deploy production service
- 15-minute validation window
- Cutover
- Post-deployment monitoring

**Duration:** 1 day + ongoing monitoring

**Total Timeline:** 2-3 weeks

## Immediate Next Steps

### Step 1: Install Test Dependencies (3 minutes)
```bash
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1
pip install -r requirements-test.txt
```

### Step 2: Run Health Check (2 minutes)
```bash
python deployment/health_check.py --all
```

Expected output:
```
PASS | Python Version
PASS | Dependencies
PASS | Environment Config
PASS | Log Directory
PASS | Database Connection
PASS | Yahoo Finance API
```

### Step 3: Run Unit Tests (5 minutes)
```bash
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
```

Expected: 100% pass, >98% coverage

### Step 4: Run Edge Case Tests (3 minutes)
```bash
pytest tests/edge_cases/ -v
```

Expected: 100% pass (20+ tests)

### Step 5: Run Performance Benchmark (10 minutes)
```bash
python monitoring/performance_benchmark.py --cycles 100 --output benchmark.json
```

Expected: >95% success rate, <8s P95 execution time

### Step 6: Review Results
```bash
# View coverage report
open htmlcov/index.html

# View benchmark report
cat benchmark.json | python -m json.tool
```

## Quick Command Reference

```bash
# Navigate to agent1 directory
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1

# Health check (all checks)
python deployment/health_check.py --all

# Health check (database only)
python deployment/health_check.py --check-db

# Health check (Yahoo Finance only)
python deployment/health_check.py --check-yfinance

# Run all unit tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_reference_levels.py -v

# Run edge case tests
pytest tests/edge_cases/test_edge_cases.py -v

# Run tests with timeout (10s per test)
pytest tests/ -v --timeout=10

# Performance benchmark (100 cycles)
python monitoring/performance_benchmark.py --cycles 100 --output benchmark.json

# 24-hour monitoring
python monitoring/continuous_monitor.py \
    --log-file /var/log/agent1/agent1_staging.log \
    --duration 24 \
    --output monitoring_report_24h.json \
    --update-interval 300

# Data quality validation (last 1 hour)
python monitoring/data_quality_validator.py --window 1

# Data quality validation (last 6 hours)
python monitoring/data_quality_validator.py --window 6

# Deploy staging service
sudo systemctl start agent1-staging.service

# Check staging service status
sudo systemctl status agent1-staging.service

# View staging logs
tail -f /var/log/agent1/agent1_staging.log

# Deploy production service
sudo systemctl start agent1-production.service
```

## Success Criteria

### Pre-Deployment Testing
- [ ] All unit tests pass (100%)
- [ ] All edge case tests pass (100%)
- [ ] Code coverage >98% for calculators
- [ ] Performance benchmark success rate >95%
- [ ] P95 execution time <8 seconds
- [ ] No memory leaks detected

### Staging Deployment
- [ ] Service starts without errors
- [ ] First cycle completes successfully
- [ ] Data appears in Supabase
- [ ] Execution time <8s per cycle
- [ ] No crashes in first hour

### 24-Hour Test
- [ ] ~1,440 cycles completed
- [ ] Success rate >95%
- [ ] P95 execution time <8s
- [ ] Service uptime >99%
- [ ] No data gaps >2 minutes
- [ ] Error recovery validated

### Production Deployment
- [ ] Pre-deployment checklist complete
- [ ] 15-minute validation window passed
- [ ] All metrics within targets
- [ ] Monitoring active
- [ ] Team handoff complete

## Troubleshooting

### Tests Failing
```bash
# Check Python version (needs 3.11+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt -r requirements-test.txt

# Run tests with verbose output
pytest tests/ -vv -s

# Run specific failing test
pytest tests/test_reference_levels.py::TestReferenceLevelCalculator::test_calculate_all_levels -vv
```

### Health Check Failing
```bash
# Check database connection
python deployment/health_check.py --check-db

# Check Yahoo Finance API
python deployment/health_check.py --check-yfinance

# Verify environment variables
cat .env

# Test manual import
python -c "from supabase_client import db_client; print('DB client OK')"
```

### Benchmark Performance Issues
```bash
# Check resource usage
top -p $(pgrep -f agent1_main.py)

# Profile specific run
python -m cProfile -s cumulative agent1_main.py

# Check network latency
ping -c 10 query1.finance.yahoo.com
```

## Support

### Documentation
- **Start Here:** `TESTING_AND_DEPLOYMENT_SUMMARY.md`
- **Technical Guide:** `deployment/TESTING_DEPLOYMENT_STRATEGY.md`
- **Step-by-Step:** `deployment/QUICK_START_GUIDE.md`
- **Checklist:** `deployment/DEPLOYMENT_CHECKLIST.md`
- **File Overview:** `TESTING_FILES_OVERVIEW.md`

### Scripts
- **Health Check:** `deployment/health_check.py`
- **Benchmark:** `monitoring/performance_benchmark.py`
- **Monitor:** `monitoring/continuous_monitor.py`
- **Validate:** `monitoring/data_quality_validator.py`

### Contact
- Engineering Team: #engineering (Slack)
- On-Call: #engineering-oncall (Slack)
- Critical: PagerDuty (production only)

## License

Copyright 2025 OpenPredict Engineering Team

---

**Version:** 1.0  
**Last Updated:** 2025-01-15  
**Status:** Ready for Testing Phase
