# Agent 1 - Production Deployment Checklist

Use this checklist to ensure all requirements are met before production deployment.

**Deployment Date:** ___________  
**Deployed By:** ___________  
**Approved By:** ___________

---

## Phase 1: Pre-Deployment Testing

### Unit Testing
- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] Code coverage >98% for calculators
- [ ] Edge case tests pass (`pytest tests/edge_cases/ -v`)
- [ ] No test failures or errors
- [ ] Test execution time <10s per test

### Integration Testing
- [ ] Integration tests with real yfinance API pass
- [ ] Integration tests with real Supabase pass
- [ ] Full pipeline test completes successfully
- [ ] Data consistency validated

### Performance Benchmarking
- [ ] 100-cycle benchmark completed
- [ ] Average execution time <5s
- [ ] P95 execution time <8s
- [ ] P99 execution time <10s
- [ ] No memory leaks detected (<100 MB growth)
- [ ] Success rate >95%

---

## Phase 2: Staging Deployment

### Environment Setup
- [ ] Staging server provisioned
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] .env.staging configured with staging credentials
- [ ] Log directory created and writable

### Service Configuration
- [ ] Systemd service file installed
- [ ] Service enabled for auto-start
- [ ] Log rotation configured
- [ ] Resource limits set (memory, CPU)

### Staging Validation
- [ ] Health check passes (`python deployment/health_check.py --all`)
- [ ] Service starts successfully
- [ ] First cycle completes without errors
- [ ] Data appears in staging Supabase
- [ ] Execution time <8s
- [ ] No crashes in first hour

---

## Phase 3: 24-Hour Continuous Test

### Test Preparation
- [ ] Staging logs cleared
- [ ] Monitoring script configured
- [ ] Test start time scheduled (after market close recommended)
- [ ] Notification channels configured

### Test Execution
- [ ] 24-hour test started
- [ ] Monitoring active
- [ ] Hourly status checks scheduled

### Error Recovery Testing
- [ ] Network disconnection test passed (5 min outage)
- [ ] Database connection loss test passed
- [ ] Graceful shutdown test passed (Ctrl+C)
- [ ] Service auto-restart verified

### Data Quality Validation
- [ ] OHLC data continuity verified (no gaps >2 min)
- [ ] Reference levels calculated consistently
- [ ] Fibonacci pivots calculated
- [ ] Liquidity events detected
- [ ] FVG patterns detected
- [ ] Hourly blocks segmented
- [ ] Market structure tracked

### Performance Validation
- [ ] ~1,440 cycles completed (24 hours)
- [ ] Success rate >95%
- [ ] Average execution time <5s
- [ ] P95 execution time <8s
- [ ] No memory leaks
- [ ] Service uptime >99%

### Test Results Review
- [ ] Monitoring report generated
- [ ] Results analyzed
- [ ] All metrics meet targets
- [ ] Issues documented and resolved

---

## Phase 4: Production Readiness

### Code Review
- [ ] Code reviewed by 2+ engineers
- [ ] Security review completed
- [ ] No hardcoded secrets or credentials
- [ ] Error handling comprehensive
- [ ] Logging appropriate (no sensitive data)

### Documentation
- [ ] README updated
- [ ] API documentation current
- [ ] Deployment guide finalized
- [ ] Runbook created
- [ ] Rollback procedures documented

### Configuration
- [ ] Production .env file created
- [ ] Production Supabase credentials validated
- [ ] Production environment variables verified
- [ ] Instrument symbol correct (NQ=F)
- [ ] Fetch interval set (60 seconds)

### Security
- [ ] Credentials stored securely (not in git)
- [ ] File permissions set correctly
- [ ] Service runs as non-root user
- [ ] Network access restricted if needed
- [ ] Supabase RLS policies configured

### Monitoring & Alerting
- [ ] Monitoring dashboards configured
- [ ] Alert rules defined
- [ ] Notification channels tested
- [ ] PagerDuty/on-call configured
- [ ] Log aggregation setup (CloudWatch/ELK)

### Backup & Recovery
- [ ] Database backup strategy defined
- [ ] Rollback procedure tested
- [ ] Disaster recovery plan documented
- [ ] Incident response playbook created

---

## Phase 5: Production Deployment

### Pre-Deployment
- [ ] Deployment window scheduled
- [ ] Team notified
- [ ] Stakeholders informed
- [ ] Rollback plan reviewed

### Deployment Execution
- [ ] Production environment provisioned
- [ ] Code deployed (specific git tag/release)
- [ ] Dependencies installed
- [ ] Configuration validated
- [ ] Service installed
- [ ] Service started successfully

### Validation Window (15 minutes)
- [ ] First cycle completes successfully
- [ ] Execution time <8s
- [ ] No errors in logs
- [ ] Data appearing in production Supabase
- [ ] Health check passes
- [ ] Metrics normal

### Cutover
- [ ] Production validated for 15+ minutes
- [ ] All metrics within targets
- [ ] Staging stopped (if applicable)
- [ ] Production auto-start enabled
- [ ] Team notified of successful deployment

---

## Phase 6: Post-Deployment

### First Hour Monitoring
- [ ] Service running stable
- [ ] No errors or crashes
- [ ] Execution time consistent
- [ ] Data quality verified
- [ ] Success rate >95%

### First 24 Hours
- [ ] Daily monitoring completed
- [ ] No critical issues
- [ ] Performance stable
- [ ] Data continuity maintained
- [ ] Alerts working correctly

### Documentation
- [ ] Deployment notes documented
- [ ] Known issues logged
- [ ] Production metrics baselined
- [ ] Runbook updated with production specifics

### Team Handoff
- [ ] On-call team briefed
- [ ] Escalation path confirmed
- [ ] Common issues documented
- [ ] Access credentials provided (securely)

---

## Rollback Criteria

**Trigger rollback immediately if:**
- [ ] Error rate >10% in first hour
- [ ] Execution time consistently >10s
- [ ] Service crashes more than 3 times
- [ ] Data corruption detected
- [ ] Memory leak causing OOM
- [ ] Critical bugs discovered

**Rollback Procedure:**
1. Stop production service: `sudo systemctl stop agent1-production.service`
2. Verify production stopped: `sudo systemctl status agent1-production.service`
3. Start previous stable version (staging): `sudo systemctl start agent1-staging.service`
4. Verify staging running: `tail -f /var/log/agent1/agent1_staging.log`
5. Notify team of rollback
6. Document incident and root cause

---

## Sign-Off

### Testing Sign-Off
- [ ] QA Engineer: _________________ Date: _______
- [ ] Lead Engineer: _________________ Date: _______

### Deployment Sign-Off
- [ ] DevOps Engineer: _________________ Date: _______
- [ ] Engineering Manager: _________________ Date: _______

### Production Approval
- [ ] Product Manager: _________________ Date: _______
- [ ] CTO/VP Engineering: _________________ Date: _______

---

## Notes

**Issues Encountered:**
```
[Document any issues found during deployment]
```

**Deviations from Plan:**
```
[Document any deviations from standard deployment procedure]
```

**Post-Deployment Actions:**
```
[Document any follow-up actions required]
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Owner:** OpenPredict Engineering Team
