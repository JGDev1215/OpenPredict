# Yahoo Finance Integration - Deployment Checklist

**Document Type:** Pre-deployment & Staging Validation Checklist
**Date:** November 16, 2025
**Target:** OpenPredict Agent 1 - 24-Hour Continuous Operation
**Status:** Ready for execution

---

## PHASE 1: PRE-DEPLOYMENT PREPARATION (Development)

### Environment Setup
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate venv: `source venv/bin/activate` (macOS/Linux)
- [ ] Activate venv: `venv\Scripts\activate` (Windows)
- [ ] Upgrade pip: `pip install --upgrade pip`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Verify yfinance version: `pip show yfinance` (should be >=0.2.38)
- [ ] If needed, upgrade yfinance: `pip install --upgrade yfinance==0.2.38`
- [ ] Create `.env` file from `.env.example`
- [ ] Verify all environment variables are populated:
  - [ ] SUPABASE_URL is set
  - [ ] SUPABASE_KEY is set
  - [ ] INSTRUMENT is set (NQ=F)
  - [ ] FETCH_INTERVAL_SECONDS is set (60)
  - [ ] LOG_LEVEL is set (INFO for production)
  - [ ] LOG_FILE path is valid

### Security Validation
- [ ] Confirm .env is in .gitignore
- [ ] Verify no hardcoded API keys in source code
- [ ] Check that credentials are not logged at INFO level
- [ ] Confirm SUPABASE_KEY is service key (not anon key)
- [ ] Review logging output for sensitive data leakage
- [ ] Enable HTTPS/TLS for all external connections (Supabase client)

### Code Quality Checks
- [ ] Run linter: `python -m pylint agent1/ --disable=all --enable=E,F` (errors only)
- [ ] Check imports: All modules can be imported without errors
- [ ] Verify type hints: Core functions have type annotations
- [ ] Review docstrings: Public functions documented
- [ ] Check PEP 8 compliance: No obvious style violations

### Dependency Validation
- [ ] Verify all dependencies are pinned to versions in requirements.txt
- [ ] Check for known security issues: `pip check`
- [ ] Confirm yfinance is compatible with pandas version
- [ ] Verify supabase-py is latest stable version
- [ ] Check APScheduler version is 3.10.4+

---

## PHASE 2: UNIT TESTING (Development)

### Data Fetcher Tests
```bash
python -m pytest agent1/tests/test_yahoo_fetcher.py -v
```
- [ ] Test fetch_ohlc returns DataFrame
- [ ] Test fetch_ohlc with empty result
- [ ] Test fetch_ohlc retry logic
- [ ] Test cache functionality
- [ ] Test data validation
- [ ] Test NaN handling
- [ ] Test timestamp validation

### Calculator Tests
```bash
python -m pytest agent1/tests/test_reference_levels.py -v
python -m pytest agent1/tests/test_fibonacci_pivots.py -v
```
- [ ] Reference level calculator tests pass
- [ ] Fibonacci pivot calculator tests pass
- [ ] Integration tests pass
- [ ] All assertions succeed

### Manual Smoke Tests
```bash
# Test 1: Import all modules
python -c "from agent1.yahoo_finance_fetcher import fetcher; print('OK')"
python -c "from agent1.supabase_client import db_client; print('OK')"
python -c "from agent1.agent1_main import Agent1; print('OK')"

# Test 2: Fetch OHLC data
python << 'EOF'
from agent1.yahoo_finance_fetcher import fetcher
df, report = fetcher.fetch_ohlc()
print(f"Fetched {len(df) if df is not None else 0} bars")
print(f"Validation: {report.is_valid}")
EOF

# Test 3: Connect to Supabase
python << 'EOF'
from agent1.supabase_client import db_client
print("Connected to Supabase successfully")
EOF

# Test 4: Run one cycle
python agent1_main.py  # Should run once and exit
```

---

## PHASE 3: STAGING ENVIRONMENT SETUP

### Server Provisioning
- [ ] Provision staging server (Ubuntu 20.04+ or macOS 12+)
- [ ] Configure firewall to allow outbound HTTPS (port 443)
- [ ] Install Python 3.10+: `python --version`
- [ ] Install pip and venv: `sudo apt-get install python3-pip python3-venv`
- [ ] Create application directory: `/opt/openpredict-agent1`
- [ ] Set directory permissions: `chown app-user:app-user /opt/openpredict-agent1`

### Staging Configuration
- [ ] Copy agent1 code to staging server
- [ ] Create .env file with staging credentials
- [ ] Set LOG_FILE to `/var/log/openpredict/agent1.log`
- [ ] Create log directory: `sudo mkdir -p /var/log/openpredict`
- [ ] Set log permissions: `sudo chown app-user:app-user /var/log/openpredict`
- [ ] Set up log rotation (see section below)
- [ ] Enable debug logging initially: `LOG_LEVEL=DEBUG`

### Log Rotation Setup
```bash
# Create /etc/logrotate.d/openpredict-agent1
sudo cat > /etc/logrotate.d/openpredict-agent1 << 'EOF'
/var/log/openpredict/agent1*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 app-user app-user
    sharedscripts
    postrotate
        # Signal app to reopen log file
        kill -HUP `cat /run/openpredict-agent1.pid` 2>/dev/null || true
    endscript
}
EOF
```

### System Monitoring Setup
- [ ] Install monitoring agent (DataDog, New Relic, or similar)
- [ ] Configure to monitor:
  - [ ] CPU usage (should be <5%)
  - [ ] Memory usage (should plateau around 100-200MB)
  - [ ] Disk I/O (log writes)
  - [ ] Network I/O (API calls)
  - [ ] Process restarts (should be 0)
- [ ] Set up alerting thresholds

### Health Check Endpoint (Optional)
- [ ] Create simple health check script that returns:
  - [ ] Last execution time
  - [ ] Success/error count
  - [ ] Memory usage
  - [ ] Cache hit rate
- [ ] Endpoint: `curl http://localhost:8000/health`

---

## PHASE 4: STAGING DEPLOYMENT

### Pre-Deployment Checklist
- [ ] Backup existing data
- [ ] Verify Supabase backups are current
- [ ] Notify team of deployment window
- [ ] Create rollback plan
- [ ] Verify staging Supabase database is accessible

### Deployment Steps
1. [ ] SSH to staging server
2. [ ] Navigate to app directory: `cd /opt/openpredict-agent1`
3. [ ] Create venv: `python3 -m venv venv`
4. [ ] Activate venv: `source venv/bin/activate`
5. [ ] Install dependencies: `pip install -r requirements.txt`
6. [ ] Update yfinance: `pip install --upgrade yfinance==0.2.38`
7. [ ] Create .env file with staging credentials
8. [ ] Run one cycle manually:
   ```bash
   python agent1_main.py  # Should complete in <8 seconds
   ```
9. [ ] Verify data in Supabase (check ohlc_data table)
10. [ ] Set up systemd service (see below)

### Systemd Service Configuration
```bash
sudo cat > /etc/systemd/system/openpredict-agent1.service << 'EOF'
[Unit]
Description=OpenPredict Agent 1 - Data Collector
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app-user
WorkingDirectory=/opt/openpredict-agent1
Environment="PATH=/opt/openpredict-agent1/venv/bin"
ExecStart=/opt/openpredict-agent1/venv/bin/python agent1_main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/openpredict/agent1.log
StandardError=append:/var/log/openpredict/agent1.log
PIDFile=/run/openpredict-agent1.pid

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openpredict-agent1
sudo systemctl start openpredict-agent1
```

### Verify Service is Running
```bash
sudo systemctl status openpredict-agent1
sudo journalctl -u openpredict-agent1 -f  # Follow logs
tail -f /var/log/openpredict/agent1.log
```

---

## PHASE 5: 24-HOUR STAGING VALIDATION

### Monitoring Schedule
- [ ] **Hour 0-1:** Monitor every 5 minutes
  - Execution time
  - Error messages
  - Data in database
- [ ] **Hour 1-6:** Monitor every 15 minutes
  - Cumulative execution time stats
  - Error rate
  - Memory trend
- [ ] **Hour 6-24:** Monitor every hour
  - Execution time distribution
  - Total error count
  - Memory usage

### Metrics to Track
Create a spreadsheet or use monitoring dashboard:

| Time | Exec Time (s) | Error Count | Memory (MB) | Cache Hit % | Status |
|------|---|---|---|---|---|
| 00:00 | 5.2 | 0 | 95 | 100 | OK |
| 01:00 | 5.3 | 0 | 98 | 87 | OK |
| ... | ... | ... | ... | ... | ... |
| 24:00 | 5.4 | 0 | 102 | 85 | OK |

### Data Quality Validation (Hourly)
Run these checks every 2 hours:
```bash
python << 'EOF'
from agent1.supabase_client import db_client

# Check latest OHLC
latest_ohlc = db_client.client.table('ohlc_data').select('*').order('timestamp', desc=True).limit(1).execute()
print(f"Latest OHLC: {latest_ohlc.data[0] if latest_ohlc.data else 'None'}")

# Check reference levels
ref_levels = db_client.client.table('reference_levels').select('*').limit(5).execute()
print(f"Reference levels count: {len(ref_levels.data)}")

# Check for errors
errors = db_client.client.table('error_log').select('*').order('created_at', desc=True).limit(5).execute()
print(f"Recent errors: {len(errors.data)}")
EOF
```

### Performance Baseline (at 24-hour mark)
- [ ] Minimum execution time: _______ seconds
- [ ] Average execution time: _______ seconds (target: <6s)
- [ ] Maximum execution time: _______ seconds (target: <8s)
- [ ] 95th percentile execution time: _______ seconds (target: <7.5s)
- [ ] 99th percentile execution time: _______ seconds (target: <8s)
- [ ] Error rate: _______ % (target: <1%)
- [ ] Cache hit rate: _______ % (target: >50%)
- [ ] Memory usage: _______ MB (should be stable)

### Success Criteria - Staging Pass
- [ ] Uptime: 99%+ (at most 14 minutes downtime in 24h)
- [ ] Execution time: Consistently <8 seconds
- [ ] Error rate: <1%
- [ ] Memory usage: Stable (no growth trend)
- [ ] Data quality: All fields populated, no obvious errors
- [ ] No API rate limit errors (429)
- [ ] No connection timeout errors
- [ ] All 8 reference levels calculated
- [ ] Database writes successful (no failed upserts)

### Failure Handling During Staging
If criteria not met:
1. [ ] Investigate error logs
2. [ ] Identify root cause
3. [ ] Implement fix in development
4. [ ] Re-test on staging
5. [ ] Repeat until success criteria met
6. [ ] Document lessons learned

---

## PHASE 6: PRODUCTION READINESS REVIEW

### Code Review Checklist
- [ ] All recommended enhancements implemented
- [ ] Data validation in place
- [ ] Error handling comprehensive
- [ ] Retry logic optimized
- [ ] Rate limiting implemented
- [ ] Memory monitoring active
- [ ] Logging appropriate for production
- [ ] No debug statements left in code
- [ ] Security review completed
- [ ] Performance benchmarks met

### Documentation Review
- [ ] README updated with production notes
- [ ] Runbook created for manual intervention
- [ ] Troubleshooting guide comprehensive
- [ ] Configuration documented
- [ ] Emergency procedures documented
- [ ] Rollback plan documented

### Stakeholder Signoff
- [ ] Development team: __________ Date: __________
- [ ] QA team: __________ Date: __________
- [ ] DevOps team: __________ Date: __________
- [ ] Product owner: __________ Date: __________

---

## PHASE 7: PRODUCTION DEPLOYMENT

### Pre-Production Steps
- [ ] Notify all teams of deployment
- [ ] Schedule during low-traffic window (if applicable)
- [ ] Create incident channel (Slack #openpredict-incidents)
- [ ] Have rollback plan ready
- [ ] Brief on-call engineer
- [ ] Test monitoring alerts

### Production Deployment
1. [ ] Deploy to production server
2. [ ] Run one cycle manually
3. [ ] Verify data in production Supabase
4. [ ] Enable systemd service
5. [ ] Monitor first 5 cycles (every 2 minutes)
6. [ ] Gradually increase monitoring interval

### Post-Deployment Validation (First Hour)
- [ ] [ ] Execution time <8 seconds ✓
- [ ] [ ] No errors in logs ✓
- [ ] [ ] Data flowing to Supabase ✓
- [ ] [ ] Alerts are functioning ✓
- [ ] [ ] Monitoring dashboard working ✓

### Production Monitoring Setup
- [ ] Real-time alerts configured:
  - [ ] Critical: Error rate >5%
  - [ ] Critical: Execution time >15s
  - [ ] Warning: Execution time >10s
  - [ ] Warning: Error rate >1%
  - [ ] Info: Cache hit rate <50%
- [ ] Daily health summary report
- [ ] Weekly performance review
- [ ] Monthly optimization review

---

## MAINTENANCE PROCEDURES

### Daily Tasks
- [ ] Review error count from previous day
- [ ] Check execution time distribution
- [ ] Verify data freshness (latest timestamp should be recent)

### Weekly Tasks
- [ ] Review execution time trends
- [ ] Check cache effectiveness
- [ ] Validate calculation accuracy (spot check)
- [ ] Review and rotate logs

### Monthly Tasks
- [ ] Update market holiday list
- [ ] Review and optimize database queries
- [ ] Analyze performance trends
- [ ] Update dependencies (if needed)
- [ ] Capacity planning review

### Incident Response
If Agent 1 stops or experiences errors:
1. [ ] Check systemd status: `sudo systemctl status openpredict-agent1`
2. [ ] Review logs: `tail -200 /var/log/openpredict/agent1.log`
3. [ ] Check Supabase connectivity
4. [ ] Check yfinance API status
5. [ ] Attempt restart: `sudo systemctl restart openpredict-agent1`
6. [ ] If restart fails, investigate root cause
7. [ ] Roll back if necessary

---

## APPENDIX: USEFUL COMMANDS

### Staging/Production Management
```bash
# View logs
tail -f /var/log/openpredict/agent1.log
tail -100 /var/log/openpredict/agent1.log | grep ERROR

# Check service status
sudo systemctl status openpredict-agent1
sudo journalctl -u openpredict-agent1 -n 50

# Restart service
sudo systemctl restart openpredict-agent1

# Check running process
ps aux | grep agent1_main

# Monitor memory
watch -n 5 'ps aux | grep python | grep agent1'

# Check disk space for logs
du -sh /var/log/openpredict/

# Monitor system resources
top -p $(pgrep -f agent1_main)
```

### Database Checks
```bash
# Check latest OHLC data
python << 'EOF'
from agent1.supabase_client import db_client
result = db_client.client.table('ohlc_data').select('*').order('timestamp', desc=True).limit(1).execute()
print(result.data)
EOF

# Check error log
python << 'EOF'
from agent1.supabase_client import db_client
result = db_client.client.table('error_log').select('*').order('created_at', desc=True).limit(10).execute()
for row in result.data:
    print(f"{row['created_at']}: {row['operation']} - {row['error_message']}")
EOF
```

### Troubleshooting
```bash
# Test yfinance connectivity
python -c "import yfinance as yf; ticker = yf.Ticker('NQ=F'); print(ticker.history(period='1d', interval='1m'))"

# Test Supabase connectivity
python -c "from agent1.supabase_client import db_client; print('Connected')"

# Check Python version
python --version

# Check installed packages
pip list | grep -E 'yfinance|supabase|pandas'
```

---

**Document Status:** Ready for use
**Last Updated:** November 16, 2025
**Review Cycle:** Every 2 weeks during development, monthly in production

