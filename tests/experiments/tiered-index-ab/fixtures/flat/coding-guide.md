# Coding Guide — Engineering Standards

## Overview

This document defines the engineering standards, coding patterns, and testing requirements for all services in the platform. All team members must follow these guidelines. Deviations require architecture review approval.

## Language and Framework Standards

### Python Services
- Python 3.11+ required for all new services
- Use `pyproject.toml` for dependency management (no `setup.py`)
- Type annotations required on all public functions
- Use `ruff` for linting (replaces flake8 + isort + black)
- Maximum line length: 100 characters
- Import ordering: stdlib → third-party → local (enforced by ruff)

### TypeScript Services
- TypeScript 5.0+ with strict mode enabled
- Use `pnpm` for package management (not npm or yarn)
- ESLint with the team's shared config (`@company/eslint-config`)
- Prettier for formatting (120 char line width)
- No `any` types — use `unknown` and narrow with type guards

### Go Services
- Go 1.21+ required
- Follow the standard project layout (`cmd/`, `internal/`, `pkg/`)
- Use `golangci-lint` with the team's config
- Error wrapping with `fmt.Errorf("context: %w", err)` — never bare returns
- Context propagation required on all public functions

## Architecture Patterns

### Service Communication
All inter-service communication uses gRPC with Protocol Buffers. REST is only for:
- Public-facing APIs (consumer mobile/web clients)
- Webhook receivers (third-party integrations)
- Health check endpoints

gRPC service definitions live in a shared `proto/` repository. Breaking changes require a new major version of the proto package.

### Data Access Patterns
- **Repository pattern** for all database access — no raw SQL in service logic
- **Unit of Work** for transactions spanning multiple repositories
- **Read replicas** for read-heavy queries (configured per-service in environment config)
- Connection pooling: min 5, max 20 per service instance (configurable)

### Circuit Breaker Pattern
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

### Event-Driven Architecture
- Use Apache Kafka for async event streaming
- Event schemas defined in Avro format, registered in Schema Registry
- Consumer groups named: `{service_name}.{purpose}` (e.g., `order-service.inventory-update`)
- Dead letter queue for events that fail processing after 3 retries
- Idempotency keys required on all event producers

### Caching Strategy
- Redis for application-level caching
- Cache-aside pattern (application manages cache, not the database)
- TTL required on all cache entries (no indefinite caching)
- Default TTL: 5 minutes for frequently changing data, 1 hour for reference data
- Cache key format: `{service}:{entity}:{id}` (e.g., `user:profile:12345`)

## Error Handling

### Error Classification
All errors must be classified into one of four categories:

| Category | HTTP Status | Action | Example |
|----------|-------------|--------|---------|
| Client error | 4xx | Return error, no retry | Invalid input, auth failure |
| Transient error | 503 | Retry with backoff | Database timeout, network glitch |
| Dependency error | 502 | Circuit breaker | Upstream service down |
| Internal error | 500 | Alert + log | Unexpected exception, data corruption |

### Retry Policy
Transient errors use exponential backoff:
- Attempt 1: immediate
- Attempt 2: wait 1 second
- Attempt 3: wait 4 seconds
- Attempt 4 (final): wait 16 seconds
- After 4 attempts: log as permanent failure, alert if error rate exceeds threshold

### Error Response Format
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

### Logging Standards
- Structured JSON logging (no plain text logs in production)
- Required fields: `timestamp`, `level`, `service`, `request_id`, `message`
- Correlation IDs propagated via `X-Request-ID` header
- **No PII in logs** — user IDs are acceptable, emails/names/addresses are not
- Log levels: DEBUG (local only), INFO (normal flow), WARN (recoverable issue), ERROR (failure)

## Testing Standards

### Unit Tests
- **Coverage requirement: >80% line coverage** for all services
- Use `pytest` (Python), `jest` (TypeScript), or `go test` (Go)
- Test file naming: `test_{module}.py` / `{module}.test.ts` / `{module}_test.go`
- Each test must be independent — no shared mutable state between tests

### Test Isolation Strategy
For database-dependent tests, use **transaction rollback isolation**:
- Each test runs inside a database transaction
- The transaction is rolled back after the test completes
- No persistent state leaks between tests
- This is faster than truncating tables and avoids sequence reset issues

For tests with external dependencies:
- Use **dependency injection** to swap real clients with mocks
- Mock at the boundary (HTTP client, gRPC stub), not deep in the service logic
- Record/replay pattern for integration tests (VCR/cassette libraries)

### Integration Tests
- Required for any service that communicates with external systems
- Use Docker Compose for local integration test environments
- Test against real database (not SQLite substitutes)
- Must run in CI — not "local only" tests

### End-to-End Tests
- Maintained by the QA team, run in staging environment
- Cover critical user journeys (login → action → verification)
- Maximum 50 e2e tests per service (keep them focused)
- Flaky test tolerance: 0% — a flaky test is immediately quarantined and fixed

### Performance Tests
- Load tests required before any new service goes to production
- Must handle 2x expected peak traffic
- Latency requirements: P50 < 100ms, P95 < 500ms, P99 < 2000ms
- Run weekly in staging, results tracked in the performance dashboard

### Test Data Principles
- **Never use production data in tests** — generate synthetic data
- Use factory patterns (Factory Boy, Faker) for test data generation
- Seed data for integration tests lives in `tests/fixtures/`
- Test data must cover edge cases: empty strings, null values, max-length strings, unicode

## Code Review Standards

### PR Requirements
- Description template must be filled (what, why, how, testing)
- Maximum PR size: 400 lines of code changes (split larger PRs)
- Self-review before requesting others
- All CI checks must pass before review

### Review Criteria
- Correctness: does the code do what it claims?
- Clarity: can another engineer understand this in 5 minutes?
- Consistency: does it follow the patterns in this guide?
- Coverage: are edge cases handled?
- Performance: any obvious bottlenecks?

### Approval Rules
- Minimum 2 approvals required for merge
- At least 1 approval must be from a code owner for the changed files
- Author cannot self-approve
- Approvals are reset on force-push (new review required)

## Configuration Management

### Environment Variables
- Use `.env` files for local development (never committed)
- Use cloud secret manager for staging/production
- All config values must have documented defaults
- Sensitive values (API keys, passwords) must be rotated every 90 days

### Feature Flags
- Use LaunchDarkly for feature flag management
- Flag naming: `{team}.{feature}.{variant}` (e.g., `payments.new-checkout.enabled`)
- All new features behind flags in production
- Flags cleaned up within 30 days of full rollout
- Emergency kill switches for all critical paths

### Input Validation
- Validate all external API input at the boundary (controller/handler layer)
- Use schema validation libraries (Pydantic, Zod, validator)
- Never trust client-side validation alone
- Sanitize all user input before database queries (parameterized queries only)
- Maximum request body size: 1MB (configurable per endpoint)

## Documentation Requirements

### Code Documentation
- Public functions require docstrings/JSDoc with parameter descriptions
- Complex algorithms need inline comments explaining the "why"
- Architecture Decision Records (ADRs) for significant design choices
- README.md required for every service with: purpose, setup, API summary

### API Documentation
- OpenAPI 3.0 spec required for all REST APIs
- Protobuf files serve as documentation for gRPC APIs
- Examples required for every endpoint
- Changelog maintained for API version changes

## Dependency Management

### Security
- Dependabot/Renovate enabled for all repositories
- Critical security updates applied within 24 hours
- High severity updates applied within 1 week
- Dependency audit run weekly in CI
- No dependencies with known critical CVEs in production

### Version Pinning
- Lock files committed (`pnpm-lock.yaml`, `poetry.lock`, `go.sum`)
- Major version updates require integration testing
- Transitive dependency conflicts resolved immediately (no "works on my machine")

## Monitoring and Observability

### Required Metrics
Every service must expose:
- Request rate (requests/second)
- Error rate (5xx responses / total responses)
- Latency percentiles (P50, P95, P99)
- Saturation (CPU, memory, connection pool usage)

### Distributed Tracing
- OpenTelemetry for trace propagation
- Trace context propagated across all service boundaries
- Sampling rate: 10% for normal traffic, 100% for errors
- Spans must include: service name, operation, duration, status
