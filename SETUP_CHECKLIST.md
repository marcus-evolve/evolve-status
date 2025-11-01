# Status Monitoring Setup Checklist

## Pre-Deployment Setup

### GitHub Repository Setup
- [ ] Create GitHub repository `evolve-status`
- [ ] Push initial code from local `evolve-status/` directory
- [ ] Enable GitHub Pages (Settings → Pages)
  - [ ] Source: Deploy from branch
  - [ ] Branch: `main`
  - [ ] Folder: `/docs`
- [ ] Verify GitHub Pages deployment (wait 1-2 minutes)
- [ ] Test status URL: `https://YOUR_USERNAME.github.io/evolve-status/status.json`

### Backend Configuration
- [ ] Update `scripts/checks.py` with Railway domain:
  ```python
  API_DOMAIN = "your-app.up.railway.app"  # Replace
  ```
- [ ] Commit and push configuration change
- [ ] Test health endpoints manually:
  ```bash
  curl https://YOUR_DOMAIN/healthz
  curl https://YOUR_DOMAIN/readyz
  ```

### iOS Configuration
- [ ] Update `AppConfiguration.swift` with GitHub Pages URL:
  ```swift
  return "https://YOUR_USERNAME.github.io/evolve-status/status.json"
  ```
- [ ] Build and run iOS app
- [ ] Check console for "Status refreshed: ok"

### GitHub Actions Setup
- [ ] Verify workflow file exists: `.github/workflows/status.yml`
- [ ] Go to Actions tab in GitHub
- [ ] Run "Publish status" workflow manually
- [ ] Verify workflow succeeds (green checkmark)
- [ ] Check that `docs/status.json` was updated
- [ ] Confirm cron schedule is active (every 2 minutes)

## Testing Phase

### Test 1: Normal Operation
- [ ] Build and run iOS app
- [ ] Verify no gate is shown
- [ ] Check console logs for status fetch
- [ ] Background and foreground app
- [ ] Verify status refreshes

### Test 2: Simulated Degradation
- [ ] Edit `docs/override.json` for degraded state
- [ ] Commit and push
- [ ] Trigger workflow manually
- [ ] Wait for GitHub Pages to update (~1 min)
- [ ] Foreground iOS app
- [ ] Verify orange "Service Degraded" gate appears
- [ ] Verify incident details shown
- [ ] Tap "Retry" button
- [ ] Verify gate persists (status still degraded)

### Test 3: Simulated Outage
- [ ] Edit `docs/override.json` for outage state
- [ ] Commit and push
- [ ] Trigger workflow manually
- [ ] Foreground iOS app
- [ ] Verify red "Service Unavailable" gate appears
- [ ] Verify outage message displayed
- [ ] Test retry functionality

### Test 4: Recovery
- [ ] Clear `docs/override.json` (set fields to null)
- [ ] Commit and push
- [ ] Trigger workflow manually
- [ ] Tap "Retry" in iOS app
- [ ] Verify gate disappears
- [ ] Verify app is fully accessible

### Test 5: Fail-Open Behavior
- [ ] Enable Airplane Mode on device/simulator
- [ ] Force quit and relaunch iOS app
- [ ] Verify app allows access (no gate shown)
- [ ] Disable Airplane Mode
- [ ] Foreground app
- [ ] Verify status refreshes

### Test 6: Cache and TTL
- [ ] Trigger degraded state
- [ ] Wait 3 minutes (TTL is 120s)
- [ ] DO NOT foreground app during wait
- [ ] After 3 minutes, foreground app
- [ ] Expected: Gate should not show (cache expired, fail-open)

### Test 7: ETag Efficiency
- [ ] Launch app (initial fetch)
- [ ] Background and foreground 5 times
- [ ] Check network logs for 304 responses
- [ ] Verify not re-downloading full status

## Pre-Production Checklist

### Documentation
- [ ] Team trained on override.json usage
- [ ] Incident response procedures documented
- [ ] Quick Start guide accessible to ops team
- [ ] Emergency contacts established

### Configuration
- [ ] Production API domain configured
- [ ] Production status URL configured
- [ ] Staging environment tested
- [ ] All placeholder URLs replaced

### Monitoring
- [ ] GitHub Actions email notifications enabled
- [ ] Status URL added to uptime monitoring
- [ ] Alerting configured for repeated workflow failures
- [ ] Escalation procedures defined

### Testing
- [ ] All 7 tests above passed
- [ ] Edge cases tested (slow networks, timeouts)
- [ ] UI reviewed in light and dark mode
- [ ] Accessibility tested

## Production Deployment

### iOS App Release
- [ ] Merge status monitoring code to main
- [ ] Build production release
- [ ] Submit to App Store / TestFlight
- [ ] Verify no regressions in other features

### Monitoring Setup
- [ ] Confirm GitHub Actions running every 2 minutes
- [ ] Verify health checks succeeding
- [ ] Check status.json updates regularly
- [ ] Monitor false positive rate (should be 0%)

### Post-Deploy Validation (24-48 hours)
- [ ] No false positive gates shown
- [ ] Status checks consistently passing
- [ ] GitHub Pages responding quickly
- [ ] No user reports of incorrect gating

## Incident Response Ready

### Procedures Documented
- [ ] How to declare incident (edit override.json)
- [ ] How to trigger immediate update (manual workflow)
- [ ] How to monitor gate rollout
- [ ] How to clear incident

### Team Prepared
- [ ] Ops team has GitHub repo access
- [ ] Ops team practiced override.json editing
- [ ] Ops team knows how to trigger workflow
- [ ] Communication templates ready

### Tools Ready
- [ ] GitHub mobile app installed (for emergency override)
- [ ] Status URL bookmarked
- [ ] Actions workflow URL bookmarked
- [ ] Health endpoints bookmarked

## Ongoing Maintenance

### Weekly
- [ ] Review GitHub Actions success rate
- [ ] Check for any anomalies in status logs
- [ ] Verify no stale incidents in override.json

### Monthly
- [ ] Review false positive/negative rates
- [ ] Tune thresholds if needed
- [ ] Update documentation with learnings
- [ ] Consider additional health checks

### Quarterly
- [ ] Review incident response times
- [ ] Optimize check frequency if needed
- [ ] Evaluate need for additional regions
- [ ] Update team training

## Troubleshooting References

If issues arise, refer to:
- [ ] `OUTAGE_GATING_QUICK_START.md` - Common fixes
- [ ] `OUTAGE_GATING_IMPLEMENTATION.md` - Deep technical details
- [ ] GitHub Actions logs - Workflow failures
- [ ] iOS console logs - Status fetch issues

## Success Criteria

Before marking as "complete":
- [ ] All setup steps completed
- [ ] All 7 tests passed
- [ ] Production deployment successful
- [ ] 48 hours of stable operation
- [ ] Zero false positives
- [ ] Team trained and confident

---

**Setup Status:** ⏳ In Progress  
**Target Completion:** [Date]  
**Completed By:** [Name]  
**Sign-off:** [Stakeholder]

