# Testing Standards

## Unit Tests
- **Coverage requirement: >80% line coverage** for all services
- Use `pytest` (Python), `jest` (TypeScript), or `go test` (Go)
- Test file naming: `test_{module}.py` / `{module}.test.ts` / `{module}_test.go`
- Each test must be independent — no shared mutable state between tests

## Test Isolation Strategy
For database-dependent tests, use **transaction rollback isolation**:
- Each test runs inside a database transaction
- The transaction is rolled back after the test completes
- No persistent state leaks between tests
- This is faster than truncating tables and avoids sequence reset issues

For tests with external dependencies:
- Use **dependency injection** to swap real clients with mocks
- Mock at the boundary (HTTP client, gRPC stub), not deep in the service logic
- Record/replay pattern for integration tests (VCR/cassette libraries)

## Integration Tests
- Required for any service that communicates with external systems
- Use Docker Compose for local integration test environments
- Test against real database (not SQLite substitutes)
- Must run in CI — not "local only" tests

## End-to-End Tests
- Maintained by the QA team, run in staging environment
- Cover critical user journeys (login → action → verification)
- Maximum 50 e2e tests per service (keep them focused)
- Flaky test tolerance: 0% — a flaky test is immediately quarantined and fixed

## Performance Tests
- Load tests required before any new service goes to production
- Must handle 2x expected peak traffic
- Latency requirements: P50 < 100ms, P95 < 500ms, P99 < 2000ms
- Run weekly in staging, results tracked in the performance dashboard

## Test Data Principles
- **Never use production data in tests** — generate synthetic data
- Use factory patterns (Factory Boy, Faker) for test data generation
- Seed data for integration tests lives in `tests/fixtures/`
- Test data must cover edge cases: empty strings, null values, max-length strings, unicode
