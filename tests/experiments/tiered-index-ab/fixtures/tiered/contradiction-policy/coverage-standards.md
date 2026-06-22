# Coverage Standards and Exception Handling

## Test Coverage Requirements

**Baseline coverage requirement:**
- All services must maintain >80% line coverage for unit tests (as defined in the Coding Guide)

**Critical service coverage requirement:**
- Services classified as "critical" must maintain **>90% line coverage**
- Critical services: payment-gateway, user-auth, order-service, billing-service
- The 90% threshold applies to both line coverage AND branch coverage for critical services

**Note:** The Coding Guide states >80% as the universal standard. This document's 90% threshold for critical services is an ADDITIONAL requirement, not a replacement. Both are correct in their scope:
- Non-critical services: >80% line coverage
- Critical services: >90% line and branch coverage

## Integration Test Coverage
- Every external API endpoint must have at least 1 integration test
- Every database migration must have a rollback test
- Coverage tracked per-service in the CI dashboard

## End-to-End Test Coverage
- Critical user journeys: 100% coverage (login, purchase, refund, account deletion)
- Non-critical journeys: best-effort, prioritized by usage frequency
- Maximum 50 e2e tests per service to prevent test suite bloat

## Approved Exceptions

### EXC-001: Legacy Reporting Service — Static API Keys
- **Standard:** API keys rotated every 90 days
- **Exception:** Reporting service uses static keys
- **Reason:** Service is internal-only, not internet-exposed
- **Risk mitigation:** Network-level access control, audit logging
- **Expiry:** Q3 2024 (remediation planned)

### EXC-002: Analytics Pipeline — Extended Batch Window
- **Standard:** Data freshness SLA of 5 minutes for real-time data
- **Exception:** Analytics pipeline batch window of 15 minutes during peak hours
- **Reason:** Kafka consumer lag increases during peak; 5-minute SLA not achievable without 3x resource scaling
- **Risk mitigation:** Dashboard shows "data delayed" banner during peak
- **Expiry:** Permanent (cost-justified)

### EXC-003: ML Model Service — Reduced Test Coverage
- **Standard:** >80% line coverage
- **Exception:** ML model service at 65% coverage
- **Reason:** ML model inference code is auto-generated from training pipeline, not amenable to unit testing
- **Risk mitigation:** Comprehensive integration tests, model validation suite, A/B testing in production
- **Expiry:** Permanent (reviewed annually)

## Exception Request Process
1. Submit exception request to architecture review board
2. Include: standard being excepted, reason, risk mitigation, proposed expiry
3. Board reviews within 5 business days
4. Approved exceptions logged here with tracking ID
5. Exceptions reviewed quarterly — expired exceptions must be resolved or renewed
