# Service-Specific Configurations

## Health Check Endpoint Format
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

## Payment Gateway Service
- Health check timeout: 5 seconds
- Circuit breaker: opens after 3 consecutive timeouts
- Health check interval: 10 seconds
- Connection pool: min 10, max 50
- Transaction timeout: 30 seconds
- PCI compliance audit: quarterly

## User Profile Service
- Health check timeout: 3 seconds
- Circuit breaker: opens after 5 consecutive timeouts
- Health check interval: 15 seconds
- Connection pool: min 5, max 30
- Cache TTL: 5 minutes for active users, 1 hour for inactive
- GDPR data export: on-demand, within 72 hours

## Notification Service
- Health check timeout: 2 seconds
- Circuit breaker: opens after 3 consecutive timeouts
- Health check interval: 10 seconds
- Batch size: 100 messages per send
- Rate limit: 1000 notifications per minute per user
- Quiet hours: respect user timezone preferences

## Reporting Service
- Health check timeout: 10 seconds (aggregation queries are slow)
- Circuit breaker: opens after 2 consecutive timeouts
- Health check interval: 30 seconds
- Query timeout: 60 seconds
- Cache TTL: 15 minutes for dashboards, 1 hour for reports
- Data freshness SLA: 5 minutes for real-time, 1 hour for batch
