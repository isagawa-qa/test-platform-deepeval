# Deployment Process

## Deployment Prerequisites
Before any deployment, ALL three conditions must be met:
1. **All CI checks green** on the branch being deployed
2. **At least 2 peer approvals** on the deployment PR
3. **No open P0/P1 bugs** against the release branch

## Deployment Pipeline
```
Code merged → CI build → Staging deploy → Staging tests
    → Canary deploy (10% traffic, 30 min)
    → Full rollout → Post-deploy monitoring (24 hours)
```

## Canary Deployment
- Start with 10% of production traffic
- Monitor for 30 minutes minimum
- Success criteria: error rate < 0.1%, latency P99 within 10% of baseline
- If criteria met: proceed to full rollout
- If criteria fail: automatic rollback within 2 minutes

## Rollback Procedure
1. Trigger rollback (automated or manual)
2. Revert to previous known-good version
3. Verify rollback successful (error rates return to baseline)
4. Page on-call engineer if rollback doesn't resolve the issue
5. Open incident if rollback fails

## Deployment Windows
- Standard deployments: Monday–Thursday, 09:00–16:00 local time
- No deployments on Fridays (frozen) or during company events
- Emergency deployments (P0 fixes): any time, with on-call approval
- Database migrations: Tuesday/Wednesday only, with DBA present
