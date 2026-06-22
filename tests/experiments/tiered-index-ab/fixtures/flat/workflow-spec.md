# Workflow Specification — Engineering Operations

## Overview

This document defines the operational workflows for the engineering team including code review, deployment, incident response, monitoring, service onboarding, and release management. All team members must follow these processes.

## Code Review Process

### PR Creation
1. Create feature branch from `main` (naming: `feat/{ticket-id}-{description}`)
2. Write code, commit with conventional commits (`feat:`, `fix:`, `chore:`)
3. Self-review: run linter and tests locally before pushing
4. Create PR using the team's PR template
5. Fill all template sections: What, Why, How, Testing, Rollback Plan

### PR Template
```markdown
## What
[One sentence describing the change]

## Why
[Business context or technical motivation]

## How
[Brief technical approach]

## Testing
[What tests were added/modified, how to verify manually]

## Rollback Plan
[How to revert if something goes wrong]
```

### Review Gates
PRs must satisfy ALL of the following before merge:

1. **CI checks green** — all linting, type checking, and tests pass
2. **Minimum 2 peer approvals** — at least 1 from a code owner
3. **No unresolved comments** — all review threads must be resolved
4. **PR size < 400 LOC** — larger PRs must be split (exceptions require tech lead approval)
5. **Description complete** — all template sections filled

### Review Timeline
- First review response: within 4 business hours
- Complete review: within 1 business day
- Urgent PRs (P0 fixes): within 2 hours, minimum 1 approval sufficient

### Merge Process
1. Squash commits to clean history (one commit per PR)
2. Merge via merge queue (not direct merge to `main`)
3. Delete feature branch after merge
4. Verify deployment to staging within 30 minutes

## Deployment Process

### Deployment Prerequisites
Before any deployment, ALL three conditions must be met:
1. **All CI checks green** on the branch being deployed
2. **At least 2 peer approvals** on the deployment PR
3. **No open P0/P1 bugs** against the release branch

### Deployment Pipeline
```
Code merged → CI build → Staging deploy → Staging tests
    → Canary deploy (10% traffic, 30 min)
    → Full rollout → Post-deploy monitoring (24 hours)
```

### Canary Deployment
- Start with 10% of production traffic
- Monitor for 30 minutes minimum
- Success criteria: error rate < 0.1%, latency P99 within 10% of baseline
- If criteria met: proceed to full rollout
- If criteria fail: automatic rollback within 2 minutes

### Rollback Procedure
1. Trigger rollback (automated or manual)
2. Revert to previous known-good version
3. Verify rollback successful (error rates return to baseline)
4. Page on-call engineer if rollback doesn't resolve the issue
5. Open incident if rollback fails

### Deployment Windows
- Standard deployments: Monday–Thursday, 09:00–16:00 local time
- No deployments on Fridays (frozen) or during company events
- Emergency deployments (P0 fixes): any time, with on-call approval
- Database migrations: Tuesday/Wednesday only, with DBA present

## Incident Response

### Severity Levels

| Level | Criteria | Response Time | Example |
|-------|----------|---------------|---------|
| P0 | Complete outage or data loss | 5 minutes | Payment service down, database corruption |
| P1 | Significant degradation (>1% error rate for >5 min) | 15 minutes | Elevated error rates, critical feature broken |
| P2 | Minor degradation, workaround exists | 1 hour | Non-critical feature broken, performance issue |
| P3 | Cosmetic or low-impact | Next business day | UI glitch, minor documentation error |

### Incident Response Steps
1. **Acknowledge** the alert within the response time for the severity level
2. **Assess severity** — use the table above, err on the side of higher severity
3. **Page on-call** if not already notified (PagerDuty rotation)
4. **Check recent deployments** (last 2 hours) — most incidents correlate with deploys
5. **If recent deploy found** → initiate rollback immediately
6. **If no recent deploy** → check dependent services, infrastructure, external providers
7. **Open incident channel** in Slack (`#inc-{date}-{description}`)
8. **Post initial assessment** — what's affected, who's investigating, ETA for mitigation
9. **Mitigate** — rollback, feature flag disable, traffic shift, or hotfix
10. **Confirm resolution** — error rate returns to baseline, affected users can access service
11. **Post-mortem** within 48 hours (blameless, action items tracked)

### Incident Communication
- Status page updated within 10 minutes for P0/P1
- Customer support notified within 15 minutes for customer-facing issues
- Executive summary within 1 hour for P0
- Post-mortem shared with engineering within 1 week

## Monitoring and Alerting

### Required Alerts (Every Service)
| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate (5xx) | >1% over 5 minutes | Page on-call |
| Latency P99 | >2 seconds | Page on-call |
| CPU usage | >80% for 10 minutes | Scale up alert |
| Memory usage | >85% for 5 minutes | Page on-call |
| Disk usage | >90% | Scale up alert |
| Health check failures | 3 consecutive | Page on-call |

### Health Check Configuration
Every service must expose a `/health` endpoint:
- **Timeout: 5 seconds** per health check request
- **Interval: 10 seconds** between checks
- **Circuit breaker: opens after 3 consecutive timeouts**
- Response must include dependency status (database, cache, upstream services)
- Health check must NOT perform expensive operations (no database queries beyond ping)

### Dashboard Requirements
- Service dashboard with the 4 golden signals (rate, errors, latency, saturation)
- Business metrics dashboard (orders/minute, signups/hour, revenue)
- Infrastructure dashboard (cluster health, node status, resource utilization)
- Dashboards reviewed weekly in ops meeting

### Log Aggregation
- All service logs shipped to centralized logging (ELK stack)
- Structured JSON format required
- Log retention: 30 days hot (searchable), 90 days warm (archived), 1 year cold
- Correlation IDs for request tracing across services
- **No PII in logs** — audit quarterly

## Release Management

### Version Strategy
- Semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: breaking API changes
- MINOR: new features, backward compatible
- PATCH: bug fixes only

### Release Process
1. **Create release branch** from `main`: `release/vX.Y.0`
2. **Run full CI suite** on release branch
3. **Update CHANGELOG.md** with version notes (using conventional commit messages)
4. **Get 2 peer approvals** on the release PR
5. **Merge to main**
6. **Tag the commit**: `vX.Y.0`
7. **Deploy to staging**, run smoke tests
8. **Deploy to production** with canary (10% traffic for 30 min)
9. **Full rollout** after canary passes
10. **Post-release monitoring** for 24 hours

### Hotfix Process
1. Branch from the release tag: `hotfix/vX.Y.1`
2. Fix the issue (minimal change only)
3. Get 1 approval (expedited review)
4. Merge to `main` and tag
5. Deploy directly (skip staging if P0)
6. Cherry-pick to any active release branches

### Release Cadence
- Minor releases: biweekly (every other Tuesday)
- Patch releases: as needed (within 24 hours for P0)
- Major releases: quarterly (planned, with migration guide)

## Service Onboarding

### New Service Requirements
Before a new service can receive production traffic, it must complete ALL of the following:

1. **Register in service catalog** — name, team, on-call rotation, documentation link
2. **Set up CI/CD pipeline** — must pass the team's pipeline template validation
3. **Configure monitoring:**
   - Error rate alerting (threshold: >1% over 5 min)
   - Latency P99 alerting (threshold: >2s)
   - Throughput alerting (sudden drop >50%)
4. **Set up logging:**
   - Structured JSON format
   - Correlation IDs propagated
   - Log levels configured (no DEBUG in production)
5. **Create runbook:**
   - Common failure modes and remediation steps
   - Dependency list with contact info
   - Scaling procedures
6. **Load test in staging:**
   - Must handle 2x expected peak traffic
   - No errors at 1x peak
   - Latency within SLA at 1.5x peak
7. **Security review:**
   - Dependency scan (no critical CVEs)
   - Auth configuration verified
   - Input validation on all external endpoints
8. **Architecture review approval** — from the architecture review board
9. **Deploy to staging** — run integration tests, verify monitoring
10. **Canary deployment to production** — 10% traffic, 30 min observation

### Service Configuration

#### Health Check Endpoint
```json
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime_seconds": 86400,
  "dependencies": {
    "database": "healthy",
    "cache": "healthy",
    "upstream_auth": "healthy"
  }
}
```

#### Service-Specific Configurations

**Payment Gateway Service:**
- Health check timeout: 5 seconds
- Circuit breaker: opens after 3 consecutive timeouts
- Health check interval: 10 seconds
- Connection pool: min 10, max 50
- Transaction timeout: 30 seconds
- PCI compliance audit: quarterly

**User Profile Service:**
- Health check timeout: 3 seconds
- Circuit breaker: opens after 5 consecutive timeouts
- Health check interval: 15 seconds
- Connection pool: min 5, max 30
- Cache TTL: 5 minutes for active users, 1 hour for inactive
- GDPR data export: on-demand, within 72 hours

**Notification Service:**
- Health check timeout: 2 seconds
- Circuit breaker: opens after 3 consecutive timeouts
- Health check interval: 10 seconds
- Batch size: 100 messages per send
- Rate limit: 1000 notifications per minute per user
- Quiet hours: respect user timezone preferences

**Reporting Service:**
- Health check timeout: 10 seconds (aggregation queries are slow)
- Circuit breaker: opens after 2 consecutive timeouts
- Health check interval: 30 seconds
- Query timeout: 60 seconds
- Cache TTL: 15 minutes for dashboards, 1 hour for reports
- Data freshness SLA: 5 minutes for real-time, 1 hour for batch

## On-Call Responsibilities

### Rotation Schedule
- Weekly rotation, handoff on Monday at 09:00 local time
- Primary and secondary on-call for every service
- Escalation: primary → secondary → team lead → engineering manager
- On-call engineer must acknowledge alerts within 5 minutes

### On-Call Duties
- Monitor alerts during on-call hours (24/7 for P0-capable services)
- Respond to incidents per the severity response times
- Update status page for customer-facing incidents
- Hand off active incidents at rotation boundary
- Document any significant events in the on-call log
