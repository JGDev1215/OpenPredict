# Agent 1 - Data Collector: Comprehensive Testing & Deployment Strategy

## Executive Summary

This document provides a complete testing and deployment strategy for the OpenPredict Agent 1 - Data Collector system. The strategy ensures production-ready deployment with >95% success rate and <8 second execution time per cycle.

**Target Metrics:**
- Success Rate: >95% over 24 hours
- Execution Time: <8 seconds per cycle
- Test Coverage: >98%
- Zero critical bugs in production

---

## 1. PRE-DEPLOYMENT TESTING PLAN

### 1.1 Unit Test Execution

**Objective:** Validate all calculator modules in isolation with 98%+ coverage.

**Commands:**
```bash
# Navigate to agent1 directory
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1

# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-timeout hypothesis

# Run unit tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Run specific test modules
pytest tests/test_reference_levels.py -v
pytest tests/test_fibonacci_pivots.py -v

# Run with timeout (fail tests taking >10s)
pytest tests/ -v --timeout=10
```

**Success Criteria:**
- All unit tests pass (100%)
- Code coverage >98% for calculator modules
- No test takes >10 seconds
- Zero failures or errors

**Coverage Targets by Module:**
- `reference_level_calculator.py`: 98%
- `fibonacci_pivot_calculator.py`: 98%
- `liquidity_event_detector.py`: 95%
- `fvg_detector.py`: 95%
- `hourly_block_segmenter.py`: 95%
- `market_structure_detector.py`: 95%
- `yahoo_finance_fetcher.py`: 90% (external dependency)
- `supabase_client.py`: 85% (external dependency)

### 1.2 Edge Case Validation

**Critical Edge Cases to Test:**

#### A. Data Quality Issues
- Empty DataFrame (no OHLC data)
- Partial data (missing bars)
- Null/NaN values in OHLC fields
- Zero volume bars
- Extreme price values (outliers)
- Duplicate timestamps
- Out-of-order timestamps

#### B. Network & API Failures
- Yahoo Finance timeout
- Yahoo Finance rate limiting (429 error)
- Network disconnection mid-fetch
- Partial data download
- Malformed API response

#### C. Database Failures
- Supabase connection timeout
- Supabase rate limiting
- Failed upsert operations
- Schema validation errors
- Duplicate key conflicts

#### D. Boundary Conditions
- Market open/close transitions
- Weekends and holidays (no trading)
- Daylight saving time changes
- First run (no historical data)
- Long running (memory leaks after 1000+ cycles)

#### E. Calculator Edge Cases
- Single bar input (insufficient data)
- Flat market (no highs/lows)
- Extreme volatility (circuit breakers)
- No liquidity events detected
- No FVG patterns found

**Test Implementation:** See `tests/edge_cases/test_edge_cases.py`

### 1.3 Mock Data Scenarios

**Mock Strategy:**
- Mock `yfinance` responses for deterministic testing
- Mock Supabase client for database operation testing
- Use `pytest-mock` for dependency injection

**Example Mock Fixtures:**
```python
# Mock yfinance data
@pytest.fixture
def mock_yfinance_success(mocker):
    mock_data = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-15 09:30', periods=100, freq='1min'),
        'open': np.random.uniform(17000, 17100, 100),
        'high': np.random.uniform(17000, 17100, 100),
        'low': np.random.uniform(17000, 17100, 100),
        'close': np.random.uniform(17000, 17100, 100),
        'volume': np.random.randint(1000, 5000, 100),
    })
    mocker.patch('yfinance.Ticker.history', return_value=mock_data)
    return mock_data

# Mock yfinance timeout
@pytest.fixture
def mock_yfinance_timeout(mocker):
    mocker.patch('yfinance.Ticker.history', side_effect=TimeoutError("Connection timeout"))

# Mock Supabase success
@pytest.fixture
def mock_supabase_success(mocker):
    mock_response = mocker.Mock()
    mock_response.execute.return_value = mocker.Mock(data=[])
    mocker.patch.object(SupabaseClient, 'upsert_ohlc', return_value=True)
```

---

## 2. STAGING DEPLOYMENT PLAN

### 2.1 Environment Setup

**Infrastructure Requirements:**
- Python 3.11+ runtime environment
- Virtual environment isolation
- Supabase staging database instance
- Log aggregation system (file-based initially)
- Process monitoring (systemd or supervisor)

**Setup Commands:**
```bash
# Create staging directory
mkdir -p ~/openpredict-staging/agent1
cd ~/openpredict-staging/agent1

# Clone repository
git clone https://github.com/your-org/OpenPredict.git .
cd agent1

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env.staging
nano .env.staging  # Edit with staging credentials
```

**Staging .env Configuration:**
```env
# Supabase Staging Configuration
SUPABASE_URL=https://staging-project.supabase.co
SUPABASE_KEY=staging-anon-key-here

# Trading Configuration
INSTRUMENT=NQ=F
FETCH_INTERVAL_SECONDS=60

# Timezone Configuration
MARKET_TIMEZONE=America/New_York
UTC_TIMEZONE=UTC

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FILE=/var/log/agent1/agent1_staging.log
```

### 2.2 Health Checks

**Pre-Start Health Checks:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(yfinance|supabase|pandas|APScheduler)"

# Test Supabase connection
python deployment/health_check.py --check-db

# Test Yahoo Finance connection
python deployment/health_check.py --check-yfinance

# Verify log directory
mkdir -p /var/log/agent1
chmod 755 /var/log/agent1
```

**Health Check Script:** See `deployment/health_check.py`

### 2.3 Monitoring Configuration

**Log Monitoring Setup:**
```bash
# Install log rotation
sudo tee /etc/logrotate.d/agent1 << 'LOGROTATE'
/var/log/agent1/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload agent1 > /dev/null 2>&1 || true
    endscript
}
LOGROTATE

# Test log rotation
logrotate -d /etc/logrotate.d/agent1
```

**Systemd Service Configuration:**
```bash
# Create systemd service
sudo tee /etc/systemd/system/agent1-staging.service << 'SERVICE'
[Unit]
Description=OpenPredict Agent 1 Data Collector (Staging)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/openpredict-staging/agent1
Environment="PATH=/home/ubuntu/openpredict-staging/agent1/venv/bin"
EnvironmentFile=/home/ubuntu/openpredict-staging/agent1/.env.staging
ExecStart=/home/ubuntu/openpredict-staging/agent1/venv/bin/python agent1_main.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/agent1/agent1_staging.log
StandardError=append:/var/log/agent1/agent1_staging_error.log

[Install]
WantedBy=multi-user.target
SERVICE

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable agent1-staging.service
```

**Start Staging Service:**
```bash
# Start service
sudo systemctl start agent1-staging.service

# Check status
sudo systemctl status agent1-staging.service

# View logs
sudo journalctl -u agent1-staging.service -f

# Or view log file
tail -f /var/log/agent1/agent1_staging.log
```

---

## 3. 24-HOUR CONTINUOUS TEST PLAN

### 3.1 Test Execution

**Objective:** Validate system stability, data quality, and performance over 24 hours (1,440 cycles).

**Test Schedule:**
```
Start Time: Friday 6:00 PM ET (after market close)
End Time:   Saturday 6:00 PM ET (24 hours later)
Total Cycles: 1,440 cycles @ 60s interval
```

**Pre-Test Preparation:**
```bash
# Ensure staging is clean
sudo systemctl stop agent1-staging.service

# Clear old logs
sudo rm -f /var/log/agent1/agent1_staging.log
sudo rm -f /var/log/agent1/agent1_staging_error.log

# Clear staging database tables (optional - for clean test)
python deployment/clear_staging_db.py --confirm

# Start monitoring script
python monitoring/continuous_monitor.py --duration 24 --output report_24h.json &

# Start agent1
sudo systemctl start agent1-staging.service

# Verify startup
tail -n 50 /var/log/agent1/agent1_staging.log
```

### 3.2 Data Quality Validation

**Real-Time Validation Queries:**

Run these SQL queries every hour to validate data integrity:

```sql
-- Check OHLC data continuity (no gaps >2 minutes)
SELECT 
    instrument,
    timestamp,
    LAG(timestamp) OVER (ORDER BY timestamp) as prev_timestamp,
    EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) as gap_seconds
FROM ohlc_data
WHERE instrument = 'NQ=F'
    AND timestamp > NOW() - INTERVAL '1 hour'
    AND EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) > 120
ORDER BY timestamp DESC;

-- Verify reference levels are being calculated
SELECT 
    level_type,
    COUNT(*) as count,
    MAX(timestamp) as latest_update
FROM reference_levels
WHERE instrument = 'NQ=F'
    AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY level_type
ORDER BY level_type;

-- Check for failed cycles (errors in error_log)
SELECT 
    timestamp,
    operation,
    error_message,
    severity
FROM error_log
WHERE component = 'agent1'
    AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- Validate data freshness (last update should be <2 minutes ago)
SELECT 
    'ohlc_data' as table_name,
    MAX(timestamp) as latest_record,
    EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) as seconds_ago
FROM ohlc_data
WHERE instrument = 'NQ=F'
UNION ALL
SELECT 
    'reference_levels' as table_name,
    MAX(timestamp) as latest_record,
    EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) as seconds_ago
FROM reference_levels
WHERE instrument = 'NQ=F';
```

**Automated Validation Script:** See `monitoring/data_quality_validator.py`

### 3.3 Performance Monitoring

**Key Metrics to Track:**

1. **Execution Time per Cycle**
   - Target: <8 seconds
   - Warning threshold: 6-8 seconds
   - Critical threshold: >8 seconds

2. **Success Rate**
   - Target: >95%
   - Calculation: (successful_cycles / total_cycles) * 100

3. **Error Rate**
   - Target: <5%
   - Types: Network errors, DB errors, calculation errors

4. **Resource Usage**
   - Memory: <500 MB
   - CPU: <20% average

**Performance Monitoring Commands:**
```bash
# Monitor process resources
watch -n 5 'ps aux | grep agent1_main.py'

# Monitor memory usage
watch -n 10 'free -h'

# Check execution times from logs
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -20

# Calculate average execution time (last 100 cycles)
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -100 | \
  awk '{print $NF}' | sed 's/s//' | \
  awk '{sum+=$1; count++} END {print "Avg:", sum/count, "s"}'

# Count errors
grep "ERROR" /var/log/agent1/agent1_staging.log | wc -l

# Calculate success rate
echo "Total cycles: $(grep 'Cycle #' /var/log/agent1/agent1_staging.log | wc -l)"
echo "Errors: $(grep 'ERROR' /var/log/agent1/agent1_staging.log | wc -l)"
```

**Real-Time Dashboard:** See `monitoring/realtime_dashboard.py`

### 3.4 Error Recovery Scenarios

**Test Scenarios:**

#### A. Network Disconnection Test
```bash
# Schedule network disconnect at random time during 24h test
# Disconnect for 5 minutes, then reconnect

# Monitor recovery
tail -f /var/log/agent1/agent1_staging.log | grep -E "(ERROR|retry|Failed)"
```

**Expected Behavior:**
- Agent1 logs network error
- Retry logic activates (3 attempts with exponential backoff)
- After network recovery, agent1 resumes normal operation
- No data corruption or crashes

#### B. Database Connection Loss
```bash
# Simulate Supabase outage by blocking connection
sudo iptables -A OUTPUT -d <supabase-ip> -j DROP

# Wait 5 minutes

# Restore connection
sudo iptables -D OUTPUT -d <supabase-ip> -j DROP
```

**Expected Behavior:**
- Database operations fail gracefully
- Errors logged to file
- System continues fetching data
- Database operations resume when connection restored

#### C. Yahoo Finance Rate Limiting
```bash
# Simulate by running multiple agent1 instances temporarily
# This will trigger rate limiting
```

**Expected Behavior:**
- Retry logic handles 429 errors
- Exponential backoff delays retries
- System recovers when rate limit expires

#### D. Graceful Shutdown
```bash
# Test Ctrl+C shutdown
# In terminal running agent1:
# Press Ctrl+C

# Or send SIGTERM
sudo systemctl stop agent1-staging.service
```

**Expected Behavior:**
- Signal handler catches SIGINT/SIGTERM
- Scheduler shuts down gracefully
- Final statistics logged
- No orphaned processes or locks

---

## 4. PERFORMANCE BENCHMARK VALIDATION

### 4.1 Execution Time Validation

**Benchmarking Methodology:**

1. **Baseline Performance Test**
   - Run 100 cycles
   - Measure execution time for each cycle
   - Calculate: min, max, mean, median, p95, p99

**Benchmark Script:**
```bash
python monitoring/performance_benchmark.py --cycles 100 --output benchmark_report.json
```

**Target Metrics:**
- Mean execution time: 3-5 seconds
- P95 execution time: <7 seconds
- P99 execution time: <8 seconds
- Max execution time: <10 seconds

**Performance Breakdown by Step:**
```
Step 1: Fetch OHLC (yfinance):         1.5 - 3.0s
Step 2: Store OHLC (Supabase):         0.3 - 0.5s
Step 3: Calculate reference levels:    0.2 - 0.4s
Step 4: Calculate Fibonacci pivots:    0.1 - 0.3s
Step 5: Detect liquidity events:       0.2 - 0.5s
Step 6: Detect FVG:                    0.1 - 0.3s
Step 7: Segment hourly blocks:         0.1 - 0.2s
Step 8: Detect market structure:       0.2 - 0.5s
Total Target:                          2.7 - 5.7s
```

**Optimization Targets:**
- If Step 1 (yfinance) >4s: Enable caching, reduce data fetch period
- If Step 2 (Supabase) >1s: Batch operations, check network latency
- If any calculator step >1s: Optimize algorithm, reduce data processing

### 4.2 Resource Usage Monitoring

**Memory Profiling:**
```bash
# Install memory profiler
pip install memory-profiler psutil

# Profile memory usage
python -m memory_profiler agent1_main.py

# Monitor over time
python monitoring/resource_monitor.py --duration 1 --interval 10 --output memory_profile.json
```

**CPU Profiling:**
```bash
# Install profiler
pip install py-spy

# Profile CPU usage (sampling)
sudo py-spy record -o cpu_profile.svg -- python agent1_main.py

# Top functions by CPU time
sudo py-spy top -- python agent1_main.py
```

**Target Resource Limits:**
- Memory: <500 MB steady state
- Memory growth: <1 MB per hour (no leaks)
- CPU: <30% average, <80% peak
- Disk I/O: <10 MB/s (mostly logs)

### 4.3 Success Rate Tracking

**Success Rate Calculation:**
```python
# From logs
total_cycles = count("Cycle #")
successful_cycles = total_cycles - count("ERROR")
success_rate = (successful_cycles / total_cycles) * 100

# Target: >95%
```

**Failure Categories:**
1. **Network Failures** (expected <2%)
   - Yahoo Finance timeout
   - Connection errors

2. **Database Failures** (expected <1%)
   - Supabase timeouts
   - Schema validation errors

3. **Data Failures** (expected <1%)
   - Empty DataFrame
   - Invalid data format

4. **System Failures** (expected <1%)
   - Out of memory
   - Unhandled exceptions

**Tracking Script:** See `monitoring/success_rate_tracker.py`

---

## 5. PRODUCTION DEPLOYMENT CHECKLIST

### 5.1 Pre-Deployment Verification

**Checklist:**

- [ ] All unit tests pass (pytest tests/ -v)
- [ ] All edge case tests pass
- [ ] Integration tests with live Supabase pass
- [ ] 24-hour continuous test completed with >95% success rate
- [ ] Performance benchmarks meet targets (<8s execution time)
- [ ] No memory leaks detected
- [ ] Log rotation configured
- [ ] Monitoring alerts configured
- [ ] Backup and rollback procedures documented
- [ ] Production environment variables configured
- [ ] Production database schema validated
- [ ] Security review completed (credentials, permissions)
- [ ] Documentation updated

**Verification Commands:**
```bash
# Run full test suite
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1
pytest tests/ -v --cov=. --cov-report=term-missing

# Verify 24h test results
python monitoring/analyze_24h_test.py --input report_24h.json

# Check performance benchmarks
python monitoring/analyze_benchmark.py --input benchmark_report.json

# Verify production config
python deployment/verify_production_config.py --env .env.production
```

### 5.2 Rollout Strategy

**Blue-Green Deployment Approach:**

1. **Preparation Phase**
   ```bash
   # Create production directory
   mkdir -p ~/openpredict-prod/agent1
   cd ~/openpredict-prod/agent1
   
   # Clone specific release tag
   git clone -b v1.0.0 https://github.com/your-org/OpenPredict.git .
   cd agent1
   
   # Setup environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure production env
   cp .env.example .env.production
   # Edit .env.production with production credentials
   ```

2. **Deploy Phase**
   ```bash
   # Create production systemd service
   sudo cp deployment/agent1-production.service /etc/systemd/system/
   sudo systemctl daemon-reload
   
   # Start production service
   sudo systemctl start agent1-production.service
   
   # Verify startup
   sudo systemctl status agent1-production.service
   tail -f /var/log/agent1/agent1_production.log
   ```

3. **Validation Phase (15 minutes)**
   ```bash
   # Monitor first 15 cycles
   python monitoring/production_validator.py --duration 15 --alerting
   
   # Check metrics
   # - Execution time <8s
   # - No errors
   # - Data being written to production DB
   ```

4. **Cutover Phase**
   ```bash
   # If validation passes:
   # Production is live!
   
   # Stop staging (if sharing resources)
   sudo systemctl stop agent1-staging.service
   
   # Enable production auto-start
   sudo systemctl enable agent1-production.service
   ```

**Rollback Procedure:**
```bash
# If issues detected:
# 1. Stop production
sudo systemctl stop agent1-production.service

# 2. Restart staging (if needed)
sudo systemctl start agent1-staging.service

# 3. Investigate logs
tail -n 500 /var/log/agent1/agent1_production.log

# 4. Revert code if needed
cd ~/openpredict-prod/agent1
git checkout <previous-tag>
pip install -r requirements.txt

# 5. Retry deployment
```

### 5.3 Monitoring Setup

**Production Monitoring Requirements:**

1. **Application Monitoring**
   - Log aggregation (AWS CloudWatch, Datadog, or file-based)
   - Error tracking (Sentry integration)
   - Performance metrics (execution time, success rate)

2. **Infrastructure Monitoring**
   - CPU, Memory, Disk usage
   - Network connectivity
   - Process health checks

3. **Business Metrics**
   - Data freshness (last OHLC timestamp)
   - Coverage (reference levels calculated)
   - Quality scores (liquidity events, FVG accuracy)

**Alert Configuration:**
```yaml
# alerts.yaml
alerts:
  - name: agent1_down
    condition: "process_status != 'running'"
    severity: critical
    notification: pagerduty
  
  - name: high_error_rate
    condition: "error_rate > 10%"
    severity: warning
    notification: slack
  
  - name: slow_execution
    condition: "execution_time_p95 > 8s"
    severity: warning
    notification: slack
  
  - name: data_staleness
    condition: "last_ohlc_age > 300s"
    severity: critical
    notification: pagerduty
  
  - name: memory_leak
    condition: "memory_usage > 750MB"
    severity: warning
    notification: slack
```

**Setup Monitoring:**
```bash
# Install monitoring agent
python monitoring/setup_monitoring.py --config monitoring/alerts.yaml

# Test alerts
python monitoring/test_alerts.py --alert agent1_down
```

### 5.4 Rollback Procedures

**Rollback Triggers:**
- Error rate >10% in first hour
- Execution time >10s consistently
- Data corruption detected
- Memory leak causing OOM
- Critical bugs discovered

**Rollback Steps:**
```bash
# 1. Stop production immediately
sudo systemctl stop agent1-production.service

# 2. Verify production stopped
sudo systemctl status agent1-production.service

# 3. Start previous stable version (staging)
sudo systemctl start agent1-staging.service

# 4. Verify staging running
tail -f /var/log/agent1/agent1_staging.log

# 5. Notify team
echo "Production rollback executed at $(date)" | mail -s "Agent1 Rollback" team@example.com

# 6. Investigate root cause
# Review production logs
tail -n 1000 /var/log/agent1/agent1_production.log > rollback_investigation_$(date +%Y%m%d_%H%M%S).log

# 7. Document incident
python deployment/incident_report.py --create --severity critical
```

**Data Integrity Check After Rollback:**
```sql
-- Check for data gaps during rollback window
SELECT 
    timestamp,
    LAG(timestamp) OVER (ORDER BY timestamp) as prev_timestamp,
    EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) as gap_seconds
FROM ohlc_data
WHERE instrument = 'NQ=F'
    AND timestamp BETWEEN '<rollback_start_time>' AND '<rollback_end_time>'
    AND EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (ORDER BY timestamp))) > 120;

-- Verify no duplicate data
SELECT timestamp, COUNT(*) 
FROM ohlc_data 
WHERE instrument = 'NQ=F'
GROUP BY timestamp 
HAVING COUNT(*) > 1;
```

---

## 6. COMPREHENSIVE TEST SUITE DESIGN

### 6.1 Additional Test Cases

**Extended Unit Tests:**

File: `tests/edge_cases/test_edge_cases.py`

Key test cases:
- `test_empty_dataframe_all_calculators()` - All calculators handle empty input
- `test_single_bar_input()` - Insufficient data scenarios
- `test_null_values_in_ohlc()` - Data quality issues
- `test_extreme_price_values()` - Outlier detection
- `test_duplicate_timestamps()` - Data deduplication
- `test_timezone_transitions()` - DST changes
- `test_market_holiday()` - No trading days
- `test_concurrent_access()` - Thread safety (if needed)

**Integration Test Extensions:**

File: `tests/test_integration_extended.py`

Key scenarios:
- `test_full_pipeline_with_real_yfinance()` - Live API test
- `test_full_pipeline_with_real_supabase()` - Live DB test
- `test_retry_logic_network_failure()` - Network recovery
- `test_retry_logic_db_failure()` - DB recovery
- `test_graceful_shutdown()` - Signal handling
- `test_memory_stability_100_cycles()` - Memory leak detection
- `test_execution_time_under_load()` - Performance under stress

**Load Testing:**

File: `tests/load_tests/test_load.py`

Scenarios:
- 1000 consecutive cycles (memory stability)
- Parallel execution (if multiple instances)
- High-frequency data (1-second intervals)
- Large datasets (30 days of 1-minute data)

### 6.2 Error Condition Tests

**Network Error Scenarios:**

```python
# tests/edge_cases/test_network_errors.py

def test_yfinance_timeout():
    """Test Yahoo Finance timeout handling"""
    # Mock timeout
    # Verify retry logic
    # Verify error logging
    
def test_yfinance_rate_limit():
    """Test rate limit (429) handling"""
    # Mock 429 response
    # Verify exponential backoff
    
def test_yfinance_malformed_response():
    """Test malformed API response"""
    # Mock invalid JSON
    # Verify error handling
    
def test_partial_data_download():
    """Test incomplete data fetch"""
    # Mock partial response
    # Verify data validation
```

**Database Error Scenarios:**

```python
# tests/edge_cases/test_database_errors.py

def test_supabase_connection_timeout():
    """Test database connection timeout"""
    
def test_supabase_schema_validation_error():
    """Test schema mismatch"""
    
def test_supabase_duplicate_key_error():
    """Test duplicate primary key handling"""
    
def test_supabase_batch_partial_failure():
    """Test partial batch upsert failure"""
```

### 6.3 Long-Running Stability Tests

**Memory Leak Detection:**

```python
# tests/stability/test_memory_leak.py

def test_memory_stability_1000_cycles():
    """Run 1000 cycles and check for memory leaks"""
    import tracemalloc
    
    tracemalloc.start()
    initial_memory = tracemalloc.get_traced_memory()
    
    agent = Agent1()
    for i in range(1000):
        agent.run_collection_cycle()
    
    final_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Memory growth should be <100 MB for 1000 cycles
    memory_growth = (final_memory[0] - initial_memory[0]) / 1024 / 1024
    assert memory_growth < 100, f"Memory leak detected: {memory_growth} MB growth"
```

**Execution Time Stability:**

```python
# tests/stability/test_execution_time.py

def test_execution_time_consistency():
    """Verify execution time doesn't degrade over time"""
    agent = Agent1()
    execution_times = []
    
    for i in range(100):
        start = time.time()
        agent.run_collection_cycle()
        execution_times.append(time.time() - start)
    
    # First 10 cycles vs last 10 cycles should be similar
    early_avg = np.mean(execution_times[:10])
    late_avg = np.mean(execution_times[-10:])
    
    # Should not degrade more than 20%
    assert late_avg < early_avg * 1.2, "Execution time degrading over cycles"
```

---

## 7. MONITORING AND ALERTING STRATEGY

### 7.1 Key Metrics to Track

**Application Metrics:**

1. **Cycle Metrics**
   - `agent1.cycle.count` - Total cycles executed
   - `agent1.cycle.success_count` - Successful cycles
   - `agent1.cycle.error_count` - Failed cycles
   - `agent1.cycle.success_rate` - Success rate percentage

2. **Performance Metrics**
   - `agent1.execution_time` - Cycle execution time (histogram)
   - `agent1.execution_time.p50` - Median execution time
   - `agent1.execution_time.p95` - 95th percentile
   - `agent1.execution_time.p99` - 99th percentile

3. **Component Metrics**
   - `agent1.yfinance.fetch_time` - Yahoo Finance fetch duration
   - `agent1.yfinance.retry_count` - Number of retries
   - `agent1.supabase.upsert_time` - Database operation duration
   - `agent1.calculator.<name>.duration` - Calculator execution time

4. **Data Metrics**
   - `agent1.ohlc.bars_fetched` - Number of OHLC bars per fetch
   - `agent1.reference_levels.count` - Reference levels calculated
   - `agent1.pivots.count` - Pivot points calculated
   - `agent1.liquidity_events.count` - Liquidity events detected
   - `agent1.fvg.count` - FVG patterns detected

5. **Error Metrics**
   - `agent1.errors.network` - Network error count
   - `agent1.errors.database` - Database error count
   - `agent1.errors.calculation` - Calculation error count
   - `agent1.errors.unknown` - Unhandled exceptions

**Infrastructure Metrics:**

1. **System Resources**
   - `system.cpu.usage` - CPU utilization percentage
   - `system.memory.usage` - Memory usage in MB
   - `system.memory.available` - Available memory
   - `system.disk.io` - Disk I/O rate

2. **Process Metrics**
   - `process.uptime` - Process uptime in seconds
   - `process.threads` - Thread count
   - `process.file_descriptors` - Open file descriptors

**Business Metrics:**

1. **Data Quality**
   - `data.freshness` - Seconds since last OHLC update
   - `data.completeness` - Percentage of expected data points
   - `data.quality_score` - Composite quality score

2. **Coverage**
   - `coverage.reference_levels` - Types of reference levels tracked
   - `coverage.sessions` - Trading sessions with data

### 7.2 Alert Conditions

**Critical Alerts (Page On-Call Engineer):**

1. **Agent1 Process Down**
   ```
   Condition: process_status != 'running'
   Window: 2 minutes
   Action: Page on-call, auto-restart attempt
   ```

2. **Data Staleness**
   ```
   Condition: time_since_last_ohlc > 300 seconds
   Window: 5 minutes
   Action: Page on-call
   Rationale: Market data is stale, trading decisions impacted
   ```

3. **High Error Rate**
   ```
   Condition: error_rate > 50% over 10 minutes
   Window: 10 minutes
   Action: Page on-call
   Rationale: System severely degraded
   ```

4. **Memory Exhaustion**
   ```
   Condition: memory_usage > 90% of limit
   Window: 5 minutes
   Action: Page on-call, prepare rollback
   ```

**Warning Alerts (Notify Team Slack):**

1. **Elevated Error Rate**
   ```
   Condition: error_rate > 10% over 30 minutes
   Window: 30 minutes
   Action: Slack notification
   ```

2. **Slow Execution**
   ```
   Condition: execution_time_p95 > 8 seconds
   Window: 15 minutes
   Action: Slack notification
   Rationale: Performance degrading, may impact data freshness
   ```

3. **Network Issues**
   ```
   Condition: yfinance_retry_rate > 20%
   Window: 15 minutes
   Action: Slack notification
   Rationale: Yahoo Finance API issues
   ```

4. **Database Slowness**
   ```
   Condition: supabase_upsert_time_p95 > 2 seconds
   Window: 15 minutes
   Action: Slack notification
   ```

5. **Reduced Coverage**
   ```
   Condition: reference_levels_count < expected_count * 0.8
   Window: 1 hour
   Action: Slack notification
   Rationale: Some calculators may be failing
   ```

### 7.3 Log Aggregation Approach

**Log Levels:**
- `DEBUG`: Detailed diagnostic info (disabled in production)
- `INFO`: Normal operational events (cycle start/end, metrics)
- `WARNING`: Abnormal but handled events (retry attempts, missing data)
- `ERROR`: Error events requiring attention
- `CRITICAL`: System-threatening failures

**Structured Logging Format:**
```json
{
  "timestamp": "2025-01-15T14:30:45.123Z",
  "level": "INFO",
  "component": "agent1",
  "cycle": 123,
  "operation": "fetch_ohlc",
  "duration_ms": 2340,
  "status": "success",
  "bars_fetched": 100,
  "message": "Successfully fetched OHLC data"
}
```

**Log Aggregation Setup:**

Option 1: **File-based + Log Shipper**
```bash
# Install filebeat
sudo apt-get install filebeat

# Configure filebeat
sudo tee /etc/filebeat/filebeat.yml << 'FILEBEAT'
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/agent1/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "agent1-logs-%{+yyyy.MM.dd}"
FILEBEAT

# Start filebeat
sudo systemctl start filebeat
```

Option 2: **CloudWatch Logs (AWS)**
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

Option 3: **Datadog**
```bash
# Install Datadog agent
DD_API_KEY=<your-api-key> DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Configure log collection
sudo tee /etc/datadog-agent/conf.d/agent1.d/conf.yaml << 'DD'
logs:
  - type: file
    path: "/var/log/agent1/*.log"
    service: "agent1"
    source: "python"
DD

sudo systemctl restart datadog-agent
```

**Query Examples:**

ElasticSearch:
```json
GET agent1-logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "range": { "timestamp": { "gte": "now-1h" }}}
      ]
    }
  },
  "aggs": {
    "errors_by_operation": {
      "terms": { "field": "operation" }
    }
  }
}
```

CloudWatch Insights:
```
fields @timestamp, level, operation, message
| filter level = "ERROR"
| stats count() by operation
| sort count desc
```

---

## APPENDIX

### A. Quick Reference Commands

**Development:**
```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test
pytest tests/test_reference_levels.py::TestReferenceLevelCalculator::test_calculate_all_levels -v

# Run edge case tests
pytest tests/edge_cases/ -v
```

**Staging:**
```bash
# Start staging
sudo systemctl start agent1-staging.service

# Check status
sudo systemctl status agent1-staging.service

# View logs
tail -f /var/log/agent1/agent1_staging.log

# Stop staging
sudo systemctl stop agent1-staging.service
```

**Production:**
```bash
# Deploy production
sudo systemctl start agent1-production.service

# Monitor production
python monitoring/realtime_dashboard.py --env production

# Check metrics
python monitoring/check_metrics.py --env production --window 1h

# Rollback
sudo systemctl stop agent1-production.service && sudo systemctl start agent1-staging.service
```

**Monitoring:**
```bash
# Calculate success rate
python monitoring/success_rate_tracker.py --window 24h

# Run performance benchmark
python monitoring/performance_benchmark.py --cycles 100

# Validate data quality
python monitoring/data_quality_validator.py --window 1h

# Generate health report
python monitoring/health_report.py --output report.json
```

### B. Success Criteria Summary

| Phase | Metric | Target | Critical Threshold |
|-------|--------|--------|-------------------|
| Unit Tests | Code Coverage | >98% | <95% |
| Unit Tests | Test Pass Rate | 100% | <100% |
| Integration | Test Pass Rate | 100% | <100% |
| 24h Test | Success Rate | >95% | <90% |
| 24h Test | Uptime | >99% | <95% |
| Performance | Avg Execution Time | <5s | >8s |
| Performance | P95 Execution Time | <7s | >10s |
| Performance | P99 Execution Time | <8s | >12s |
| Resources | Memory Usage | <500MB | >750MB |
| Resources | CPU Usage | <30% | >80% |
| Data Quality | Freshness | <2min | >5min |
| Data Quality | Completeness | >98% | <90% |

### C. Contact and Escalation

**Escalation Path:**
1. On-call Engineer (immediate response)
2. Team Lead (within 30 minutes)
3. Engineering Manager (within 1 hour)

**Communication Channels:**
- Slack: #agent1-alerts (automated alerts)
- Slack: #engineering-oncall (manual escalation)
- PagerDuty: Critical alerts only

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Owner:** OpenPredict Engineering Team
