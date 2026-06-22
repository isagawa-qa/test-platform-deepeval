# Architecture Patterns and Error Handling

## Service Communication
All inter-service communication uses gRPC with Protocol Buffers. REST is only for:
- Public-facing APIs (consumer mobile/web clients)
- Webhook receivers (third-party integrations)
- Health check endpoints

gRPC service definitions live in a shared `proto/` repository. Breaking changes require a new major version of the proto package.

## Data Access Patterns
- **Repository pattern** for all database access — no raw SQL in service logic
- **Unit of Work** for transactions spanning multiple repositories
- **Read replicas** for read-heavy queries (configured per-service in environment config)
- Connection pooling: min 5, max 20 per service instance (configurable)

## Circuit Breaker Pattern
All external service calls (HTTP, gRPC, database) must use a circuit breaker:
- **Closed state:** normal operation, requests flow through
- **Open state:** after 3 consecutive failures, all requests fail fast for 30 seconds
- **Half-open state:** after 30 seconds, allow 1 test request; if it succeeds, close the circuit

Configuration per external dependency:
```yaml
circuit_breaker:
  failure_threshold: 3
  recovery_timeout_seconds: 30
  test_request_count: 1
```

## Event-Driven Architecture
- Use Apache Kafka for async event streaming
- Event schemas defined in Avro format, registered in Schema Registry
- Consumer groups named: `{service_name}.{purpose}` (e.g., `order-service.inventory-update`)
- Dead letter queue for events that fail processing after 3 retries
- Idempotency keys required on all event producers

## Caching Strategy
- Redis for application-level caching
- Cache-aside pattern (application manages cache, not the database)
- TTL required on all cache entries (no indefinite caching)
- Default TTL: 5 minutes for frequently changing data, 1 hour for reference data
- Cache key format: `{service}:{entity}:{id}` (e.g., `user:profile:12345`)

## Error Classification
All errors must be classified into one of four categories:

| Category | HTTP Status | Action | Example |
|----------|-------------|--------|---------|
| Client error | 4xx | Return error, no retry | Invalid input, auth failure |
| Transient error | 503 | Retry with backoff | Database timeout, network glitch |
| Dependency error | 502 | Circuit breaker | Upstream service down |
| Internal error | 500 | Alert + log | Unexpected exception, data corruption |

## Retry Policy
Transient errors use exponential backoff:
- Attempt 1: immediate
- Attempt 2: wait 1 second
- Attempt 3: wait 4 seconds
- Attempt 4 (final): wait 16 seconds
- After 4 attempts: log as permanent failure, alert if error rate exceeds threshold

## Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      {"field": "email", "issue": "Invalid format"}
    ],
    "request_id": "uuid-for-tracing"
  }
}
```

## Logging Standards
- Structured JSON logging (no plain text logs in production)
- Required fields: `timestamp`, `level`, `service`, `request_id`, `message`
- Correlation IDs propagated via `X-Request-ID` header
- **No PII in logs** — user IDs are acceptable, emails/names/addresses are not
- Log levels: DEBUG (local only), INFO (normal flow), WARN (recoverable issue), ERROR (failure)

## Input Validation
- Validate all external API input at the boundary (controller/handler layer)
- Use schema validation libraries (Pydantic, Zod, validator)
- Never trust client-side validation alone
- Sanitize all user input before database queries (parameterized queries only)
- Maximum request body size: 1MB (configurable per endpoint)

## Monitoring and Observability

### Required Metrics
Every service must expose: request rate, error rate, latency percentiles (P50, P95, P99), saturation (CPU, memory, connection pool usage).

### Distributed Tracing
- OpenTelemetry for trace propagation
- Trace context propagated across all service boundaries
- Sampling rate: 10% for normal traffic, 100% for errors
- Spans must include: service name, operation, duration, status
