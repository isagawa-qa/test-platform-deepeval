# Monitoring and Alerting

## Required Alerts (Every Service)
| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate (5xx) | >1% over 5 minutes | Page on-call |
| Latency P99 | >2 seconds | Page on-call |
| CPU usage | >80% for 10 minutes | Scale up alert |
| Memory usage | >85% for 5 minutes | Page on-call |
| Disk usage | >90% | Scale up alert |
| Health check failures | 3 consecutive | Page on-call |

## Health Check Configuration
Every service must expose a `/health` endpoint:
- **Timeout: 5 seconds** per health check request
- **Interval: 10 seconds** between checks
- **Circuit breaker: opens after 3 consecutive timeouts**
- Response must include dependency status (database, cache, upstream services)
- Health check must NOT perform expensive operations (no database queries beyond ping)

## Dashboard Requirements
- Service dashboard with the 4 golden signals (rate, errors, latency, saturation)
- Business metrics dashboard (orders/minute, signups/hour, revenue)
- Infrastructure dashboard (cluster health, node status, resource utilization)
- Dashboards reviewed weekly in ops meeting

## Log Aggregation
- All service logs shipped to centralized logging (ELK stack)
- Structured JSON format required
- Log retention: 30 days hot (searchable), 90 days warm (archived), 1 year cold
- Correlation IDs for request tracing across services
- **No PII in logs** — audit quarterly

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
