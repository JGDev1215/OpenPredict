# Deployment & Testing Resources

This directory contains comprehensive testing and deployment resources for Agent 1 - Data Collector.

## Contents

### Documentation
- **TESTING_DEPLOYMENT_STRATEGY.md** - Complete testing and deployment strategy with detailed procedures
- **QUICK_START_GUIDE.md** - Step-by-step guide for testing and deployment
- **DEPLOYMENT_CHECKLIST.md** - Production deployment checklist with sign-off

### Scripts
- **health_check.py** - System health check script
  ```bash
  python health_check.py --all
  ```

### Service Files
- **agent1-staging.service** - Systemd service for staging environment
- **agent1-production.service** - Systemd service for production environment

## Quick Reference

### Run Health Check
```bash
cd /Users/soonjeongguan/Desktop/Repository/CLAUDECODE/OpenPredict/agent1
python deployment/health_check.py --all
```

### Run Unit Tests
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Run Performance Benchmark
```bash
python monitoring/performance_benchmark.py --cycles 100 --output benchmark_report.json
```

### Start 24-Hour Monitoring
```bash
python monitoring/continuous_monitor.py \
    --log-file /var/log/agent1/agent1_staging.log \
    --duration 24 \
    --output monitoring_report_24h.json
```

### Validate Data Quality
```bash
python monitoring/data_quality_validator.py --window 1
```

## Deployment Phases

1. **Pre-Deployment Testing**
   - Install dependencies
   - Run health checks
   - Execute unit tests
   - Run performance benchmarks

2. **Staging Deployment**
   - Setup staging environment
   - Install systemd service
   - Validate deployment

3. **24-Hour Continuous Test**
   - Start monitoring
   - Run continuous test
   - Validate data quality
   - Test error recovery

4. **Production Deployment**
   - Pre-deployment verification
   - Deploy to production
   - Validation window
   - Cutover

## Target Metrics

- **Success Rate:** >95%
- **Execution Time:** <8 seconds (P95)
- **Test Coverage:** >98%
- **Uptime:** >99%

## Support

For detailed instructions, see:
- TESTING_DEPLOYMENT_STRATEGY.md (comprehensive guide)
- QUICK_START_GUIDE.md (step-by-step walkthrough)
- DEPLOYMENT_CHECKLIST.md (production checklist)

---

**Last Updated:** 2025-01-15
