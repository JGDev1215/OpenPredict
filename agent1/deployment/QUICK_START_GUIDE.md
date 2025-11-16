# Agent 1 - Quick Start Guide

This guide provides step-by-step instructions to test and deploy Agent 1 from development to production.

## Table of Contents
1. [Pre-Deployment Testing](#pre-deployment-testing)
2. [Staging Deployment](#staging-deployment)
3. [24-Hour Continuous Test](#24-hour-continuous-test)
4. [Production Deployment](#production-deployment)

---

## Pre-Deployment Testing

### Step 1: Install Dependencies

```bash
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1

# Create virtual environment (if not exists)
python3.11 -m venv venv
source venv/bin/activate

# Install runtime dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Required variables:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key-here
# INSTRUMENT=NQ=F
# FETCH_INTERVAL_SECONDS=60
```

### Step 3: Run Health Check

```bash
# Run comprehensive health check
python deployment/health_check.py --all

# Expected output:
#   PASS | Python Version
#   PASS | Dependencies
#   PASS | Environment Config
#   PASS | Log Directory
#   PASS | Database Connection
#   PASS | Yahoo Finance API
```

### Step 4: Run Unit Tests

```bash
# Run all unit tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Run specific test modules
pytest tests/test_reference_levels.py -v
pytest tests/test_fibonacci_pivots.py -v
pytest tests/test_integration.py -v

# Run edge case tests
pytest tests/edge_cases/test_edge_cases.py -v

# Check coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

**Success Criteria:**
- All tests pass (100%)
- Coverage >98% for calculator modules
- No failures or errors

### Step 5: Run Performance Benchmark

```bash
# Run 100-cycle benchmark
python monitoring/performance_benchmark.py --cycles 100 --output benchmark_report.json

# Review results
cat benchmark_report.json | python -m json.tool
```

**Success Criteria:**
- Success rate >95%
- Average execution time <5s
- P95 execution time <8s
- No memory leaks

---

## Staging Deployment

### Step 1: Setup Staging Environment

```bash
# On staging server
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
```

### Step 2: Configure Staging Environment

```bash
# Create staging env file
cp .env.example .env.staging

# Edit with staging credentials
nano .env.staging

# Set staging-specific values:
# SUPABASE_URL=https://staging-project.supabase.co
# SUPABASE_KEY=staging-anon-key
# LOG_FILE=/var/log/agent1/agent1_staging.log
```

### Step 3: Setup Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/agent1
sudo chown $USER:$USER /var/log/agent1
chmod 755 /var/log/agent1
```

### Step 4: Install Systemd Service

```bash
# Copy service file
sudo cp deployment/agent1-staging.service /etc/systemd/system/

# Edit paths in service file if needed
sudo nano /etc/systemd/system/agent1-staging.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable agent1-staging.service
```

### Step 5: Start Staging Service

```bash
# Start service
sudo systemctl start agent1-staging.service

# Check status
sudo systemctl status agent1-staging.service

# View logs
tail -f /var/log/agent1/agent1_staging.log

# Or use journalctl
sudo journalctl -u agent1-staging.service -f
```

### Step 6: Verify Staging Deployment

```bash
# Wait 5 minutes, then check logs
tail -n 100 /var/log/agent1/agent1_staging.log

# Verify data in Supabase
python monitoring/data_quality_validator.py --window 1

# Check performance
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -20
```

**Success Criteria:**
- Service running without errors
- Data appearing in Supabase tables
- Execution time <8s per cycle
- No crashes or restarts

---

## 24-Hour Continuous Test

### Step 1: Prepare for 24h Test

```bash
# Stop staging service
sudo systemctl stop agent1-staging.service

# Clear logs for clean test
sudo rm -f /var/log/agent1/agent1_staging.log
sudo rm -f /var/log/agent1/agent1_staging_error.log

# Optional: Clear staging database tables
# python deployment/clear_staging_db.py --confirm
```

### Step 2: Start Monitoring

```bash
# In a separate terminal/screen session
screen -S agent1-monitor

# Start continuous monitor (24 hours)
python monitoring/continuous_monitor.py \
    --log-file /var/log/agent1/agent1_staging.log \
    --duration 24 \
    --output monitoring_report_24h.json \
    --update-interval 300

# Detach from screen: Ctrl+A, then D
```

### Step 3: Start 24h Test

```bash
# Start staging service
sudo systemctl start agent1-staging.service

# Verify startup
tail -f /var/log/agent1/agent1_staging.log
# Press Ctrl+C after seeing first successful cycle
```

### Step 4: Monitor Progress

```bash
# Reattach to monitor
screen -r agent1-monitor

# Or check logs periodically
tail -n 50 /var/log/agent1/agent1_staging.log

# Check status
sudo systemctl status agent1-staging.service

# Count cycles
grep "Cycle #" /var/log/agent1/agent1_staging.log | wc -l

# Count errors
grep "ERROR" /var/log/agent1/agent1_staging.log | wc -l

# Calculate success rate
echo "Cycles: $(grep 'Cycle #' /var/log/agent1/agent1_staging.log | wc -l)"
echo "Errors: $(grep 'ERROR' /var/log/agent1/agent1_staging.log | wc -l)"
```

### Step 5: Run Data Quality Checks

```bash
# Run validation every few hours
python monitoring/data_quality_validator.py --window 6

# Check for data gaps
# See TESTING_DEPLOYMENT_STRATEGY.md for SQL queries
```

### Step 6: Test Error Recovery

**During the 24h test, simulate failures:**

#### Network Disconnection (5 minutes)
```bash
# Disconnect network (example - adjust for your setup)
sudo systemctl stop NetworkManager

# Wait 5 minutes

# Reconnect
sudo systemctl start NetworkManager

# Verify recovery in logs
grep -A 10 "ERROR" /var/log/agent1/agent1_staging.log
```

#### Graceful Shutdown
```bash
# Stop service
sudo systemctl stop agent1-staging.service

# Check logs for graceful shutdown
tail -n 20 /var/log/agent1/agent1_staging.log
# Should see: "Stopping Agent 1..." and final statistics

# Restart
sudo systemctl start agent1-staging.service
```

### Step 7: Review 24h Test Results

```bash
# After 24 hours, stop service
sudo systemctl stop agent1-staging.service

# Review monitoring report
cat monitoring_report_24h.json | python -m json.tool

# Generate summary
python monitoring/analyze_24h_test.py --input monitoring_report_24h.json

# Check final statistics
tail -n 100 /var/log/agent1/agent1_staging.log
```

**Success Criteria:**
- Total cycles: ~1,440 (24 hours * 60 cycles/hour)
- Success rate: >95%
- P95 execution time: <8s
- Service uptime: >99%
- Data quality: No significant gaps
- Error recovery: System recovered from simulated failures

---

## Production Deployment

### Step 1: Pre-Deployment Checklist

```bash
# Verify all tests passed
# - [ ] Unit tests: 100% pass
# - [ ] Edge case tests: 100% pass
# - [ ] Integration tests: 100% pass
# - [ ] 24h continuous test: >95% success rate
# - [ ] Performance benchmarks: <8s execution time
# - [ ] No memory leaks detected

# Verify configuration
python deployment/verify_production_config.py --env .env.production
```

### Step 2: Setup Production Environment

```bash
# On production server
mkdir -p ~/openpredict-prod/agent1
cd ~/openpredict-prod/agent1

# Clone specific release tag
git clone -b v1.0.0 https://github.com/your-org/OpenPredict.git .
cd agent1

# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure production
cp .env.example .env.production
nano .env.production
# Use PRODUCTION Supabase credentials
```

### Step 3: Install Production Service

```bash
# Copy service file
sudo cp deployment/agent1-production.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/agent1-production.service

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable agent1-production.service
```

### Step 4: Deploy Production

```bash
# Start production service
sudo systemctl start agent1-production.service

# Monitor startup closely
tail -f /var/log/agent1/agent1_production.log
```

### Step 5: Validation Window (15 minutes)

```bash
# Run production validator
python monitoring/production_validator.py --duration 15 --alerting

# Check first 15 cycles
# - Execution time <8s
# - No errors
# - Data being written to production DB
```

### Step 6: Cutover

**If validation passes:**
```bash
# Production is live!
echo "Production deployment successful at $(date)" | mail -s "Agent1 Production" team@example.com

# Stop staging (if needed)
sudo systemctl stop agent1-staging.service

# Confirm auto-start enabled
sudo systemctl is-enabled agent1-production.service
```

**If validation fails:**
```bash
# Rollback immediately
sudo systemctl stop agent1-production.service

# Restart staging
sudo systemctl start agent1-staging.service

# Investigate
tail -n 500 /var/log/agent1/agent1_production.log > rollback_$(date +%Y%m%d_%H%M%S).log
```

### Step 7: Post-Deployment Monitoring

```bash
# Monitor for first hour
watch -n 60 'systemctl status agent1-production.service'

# Check metrics every 15 minutes
watch -n 900 'python monitoring/check_metrics.py --env production --window 1h'

# Setup automated monitoring (cron job)
crontab -e

# Add:
# */15 * * * * python ~/openpredict-prod/agent1/monitoring/check_metrics.py --env production --window 1h >> /var/log/agent1/monitoring.log 2>&1
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u agent1-staging.service -n 50

# Check file permissions
ls -la ~/openpredict-staging/agent1/

# Test manually
cd ~/openpredict-staging/agent1
source venv/bin/activate
python agent1_main.py
```

### High error rate
```bash
# Count errors by type
grep "ERROR" /var/log/agent1/agent1_staging.log | cut -d':' -f4 | sort | uniq -c

# Check network connectivity
ping -c 5 query1.finance.yahoo.com

# Check database connectivity
python deployment/health_check.py --check-db
```

### Slow execution time
```bash
# Profile performance
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -100

# Check resource usage
top -p $(pgrep -f agent1_main.py)

# Run benchmark
python monitoring/performance_benchmark.py --cycles 50
```

### Memory issues
```bash
# Check memory usage
ps aux | grep agent1_main.py

# Monitor over time
watch -n 60 'ps aux | grep agent1_main.py'

# Restart service to clear memory
sudo systemctl restart agent1-staging.service
```

---

## Next Steps After Deployment

1. **Setup Monitoring Dashboards**
   - Configure CloudWatch/Datadog/Grafana
   - Create custom dashboards for key metrics
   - Setup alert notifications (Slack, PagerDuty)

2. **Configure Log Aggregation**
   - Setup ELK stack or CloudWatch Logs
   - Create log queries for common issues
   - Setup automated log analysis

3. **Performance Optimization**
   - Profile bottlenecks
   - Optimize slow calculators
   - Implement caching strategies

4. **Backup and Disaster Recovery**
   - Setup database backups
   - Document recovery procedures
   - Test rollback scenarios

5. **Documentation**
   - Update runbook with production specifics
   - Document common issues and resolutions
   - Create on-call playbook

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Owner:** OpenPredict Engineering Team
