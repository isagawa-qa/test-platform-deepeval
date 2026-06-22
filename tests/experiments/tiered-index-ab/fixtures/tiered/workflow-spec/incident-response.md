# Incident Response

## Severity Levels

| Level | Criteria | Response Time | Example |
|-------|----------|---------------|---------|
| P0 | Complete outage or data loss | 5 minutes | Payment service down, database corruption |
| P1 | Significant degradation (>1% error rate for >5 min) | 15 minutes | Elevated error rates, critical feature broken |
| P2 | Minor degradation, workaround exists | 1 hour | Non-critical feature broken, performance issue |
| P3 | Cosmetic or low-impact | Next business day | UI glitch, minor documentation error |

## Incident Response Steps
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

## Incident Communication
- Status page updated within 10 minutes for P0/P1
- Customer support notified within 15 minutes for customer-facing issues
- Executive summary within 1 hour for P0
- Post-mortem shared with engineering within 1 week
