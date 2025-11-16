# Monitoring & Validation Tools

This directory contains monitoring, benchmarking, and validation tools for Agent 1.

## Scripts

### continuous_monitor.py
Real-time monitoring script for 24-hour continuous testing.

**Usage:**
```bash
python continuous_monitor.py \
    --log-file /var/log/agent1/agent1_staging.log \
    --duration 24 \
    --output monitoring_report_24h.json \
    --update-interval 300
```

**Features:**
- Tracks cycle count, success rate, errors
- Calculates execution time statistics
- Generates hourly performance reports
- Creates comprehensive JSON report
- Real-time status updates

**Output:** `monitoring_report_24h.json`

---

### performance_benchmark.py
Performance benchmarking tool to measure execution time and resource usage.

**Usage:**
```bash
python performance_benchmark.py --cycles 100 --output benchmark_report.json
```

**Features:**
- Measures execution time (mean, median, P95, P99)
- Tracks memory usage and growth
- Detects memory leaks
- Calculates success rate
- Generates assessment report

**Output:** `benchmark_report.json`

---

### data_quality_validator.py
Validates data integrity in Supabase database.

**Usage:**
```bash
python data_quality_validator.py --window 1  # Last 1 hour
```

**Features:**
- Checks OHLC data continuity (gaps)
- Verifies reference levels calculated
- Validates data freshness (<5 min)
- Detects duplicate records
- Reports data quality issues

**Exit Codes:**
- 0: All checks passed
- 1: Issues detected

---

## Example Workflows

### Pre-Deployment Benchmark
```bash
# Run 100-cycle performance test
python monitoring/performance_benchmark.py --cycles 100 --output pre_deploy_benchmark.json

# Review results
cat pre_deploy_benchmark.json | python -m json.tool

# Check if metrics meet targets
# - success_rate >= 95%
# - execution_time.p95 < 8.0
# - memory.growth_mb < 100
```

### 24-Hour Continuous Test
```bash
# Terminal 1: Start monitoring
python monitoring/continuous_monitor.py \
    --log-file /var/log/agent1/agent1_staging.log \
    --duration 24 \
    --output report_24h.json

# Terminal 2: Start agent1
sudo systemctl start agent1-staging.service

# Monitor progress
tail -f /var/log/agent1/agent1_staging.log
```

### Hourly Data Quality Check
```bash
# Setup cron job for hourly validation
crontab -e

# Add:
0 * * * * python ~/openpredict/agent1/monitoring/data_quality_validator.py --window 1 >> /var/log/agent1/validation.log 2>&1
```

### Real-time Performance Monitoring
```bash
# Monitor execution time in real-time
watch -n 10 'grep "Completed in" /var/log/agent1/agent1_staging.log | tail -20'

# Calculate average execution time (last 100 cycles)
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -100 | \
  awk -F'in ' '{print $2}' | sed 's/s.*//' | \
  awk '{sum+=$1; count++} END {print "Avg:", sum/count, "s"}'
```

## Monitoring Metrics

### Key Performance Indicators (KPIs)

**Execution Time:**
- Target: <8 seconds (P95)
- Warning: 6-8 seconds
- Critical: >8 seconds

**Success Rate:**
- Target: >95%
- Warning: 90-95%
- Critical: <90%

**Data Freshness:**
- Target: <2 minutes
- Warning: 2-5 minutes
- Critical: >5 minutes

**Memory Usage:**
- Target: <500 MB
- Warning: 500-750 MB
- Critical: >750 MB

### Alert Conditions

**Critical Alerts:**
- Agent1 process down (>2 min)
- Data staleness >5 min
- Error rate >50%
- Memory exhaustion >90%

**Warning Alerts:**
- Error rate >10%
- Execution time P95 >8s
- Network retry rate >20%
- Database slowness

## Output Formats

### Benchmark Report (JSON)
```json
{
  "benchmark_metadata": {
    "timestamp": "2025-01-15T14:30:00Z",
    "cycles": 100
  },
  "summary": {
    "total_cycles": 100,
    "successful_cycles": 98,
    "success_rate": 98.0
  },
  "execution_time": {
    "mean": 4.52,
    "median": 4.23,
    "p95": 7.12,
    "p99": 7.89
  },
  "assessment": {
    "success_rate_pass": true,
    "avg_time_pass": true,
    "p95_time_pass": true
  }
}
```

### Monitoring Report (JSON)
```json
{
  "test_metadata": {
    "start_time": "2025-01-15T18:00:00Z",
    "duration_hours": 24
  },
  "summary": {
    "total_cycles": 1440,
    "successful_cycles": 1398,
    "success_rate": 97.08
  },
  "performance": {
    "avg_execution_time": 4.32,
    "p95_execution_time": 6.87,
    "p99_execution_time": 7.45
  },
  "assessment": {
    "overall_pass": true
  }
}
```

## Troubleshooting

### Monitor shows low success rate
```bash
# Check error types
grep "ERROR" /var/log/agent1/agent1_staging.log | cut -d':' -f4 | sort | uniq -c

# Test network connectivity
python deployment/health_check.py --check-yfinance

# Test database connectivity
python deployment/health_check.py --check-db
```

### High execution time
```bash
# Profile recent cycles
grep "Completed in" /var/log/agent1/agent1_staging.log | tail -50

# Check resource usage
top -p $(pgrep -f agent1_main.py)

# Run detailed benchmark
python monitoring/performance_benchmark.py --cycles 50
```

### Data quality issues
```bash
# Run validation
python monitoring/data_quality_validator.py --window 6

# Check database logs
tail -f /var/log/agent1/agent1_staging.log | grep "Stored"

# Verify Supabase connection
python deployment/health_check.py --check-db
```

---

**Last Updated:** 2025-01-15
