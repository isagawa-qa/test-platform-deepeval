# Contradiction Policy — Quality Standards and Exception Handling

## Overview

This document defines quality standards, coverage requirements, and exception handling policies. It serves as the authoritative source for thresholds and standards that may appear (sometimes with different values) in other documentation. When conflicts arise, this document takes precedence.

## Coverage Standards

### Test Coverage Requirements

**Baseline coverage requirement:**
- All services must maintain >80% line coverage for unit tests (as defined in the Coding Guide)

**Critical service coverage requirement:**
- Services classified as "critical" must maintain **>90% line coverage**
- Critical services: payment-gateway, user-auth, order-service, billing-service
- The 90% threshold applies to both line coverage AND branch coverage for critical services

**Note:** The Coding Guide states >80% as the universal standard. This document's 90% threshold for critical services is an ADDITIONAL requirement, not a replacement. Both are correct in their scope:
- Non-critical services: >80% line coverage
- Critical services: >90% line and branch coverage

### Integration Test Coverage
- Every external API endpoint must have at least 1 integration test
- Every database migration must have a rollback test
- Coverage tracked per-service in the CI dashboard

### End-to-End Test Coverage
- Critical user journeys: 100% coverage (login, purchase, refund, account deletion)
- Non-critical journeys: best-effort, prioritized by usage frequency
- Maximum 50 e2e tests per service to prevent test suite bloat

## Exception Handling

### Approved Exceptions
The following exceptions to standard policies have been approved by the architecture review board:

#### EXC-001: Legacy Reporting Service — Static API Keys
- **Standard:** API keys rotated every 90 days
- **Exception:** Reporting service uses static keys
- **Reason:** Service is internal-only, not internet-exposed
- **Risk mitigation:** Network-level access control, audit logging
- **Expiry:** Q3 2024 (remediation planned)

#### EXC-002: Analytics Pipeline — Extended Batch Window
- **Standard:** Data freshness SLA of 5 minutes for real-time data
- **Exception:** Analytics pipeline batch window of 15 minutes during peak hours
- **Reason:** Kafka consumer lag increases during peak; 5-minute SLA not achievable without 3x resource scaling
- **Risk mitigation:** Dashboard shows "data delayed" banner during peak
- **Expiry:** Permanent (cost-justified)

#### EXC-003: ML Model Service — Reduced Test Coverage
- **Standard:** >80% line coverage
- **Exception:** ML model service at 65% coverage
- **Reason:** ML model inference code is auto-generated from training pipeline, not amenable to unit testing
- **Risk mitigation:** Comprehensive integration tests, model validation suite, A/B testing in production
- **Expiry:** Permanent (reviewed annually)

### Exception Request Process
1. Submit exception request to architecture review board
2. Include: standard being excepted, reason, risk mitigation, proposed expiry
3. Board reviews within 5 business days
4. Approved exceptions logged here with tracking ID
5. Exceptions reviewed quarterly — expired exceptions must be resolved or renewed

## Quality Gates by Environment

### Development
- Linter passes (no errors, warnings acceptable)
- Unit tests pass
- Code compiles/builds successfully

### Staging
- All development gates pass
- Integration tests pass
- Performance benchmarks within SLA
- Security scan (no critical or high findings)

### Production
- All staging gates pass
- Canary deployment successful (30 min, <0.1% error rate)
- Monitoring configured and alerting verified
- Rollback tested in staging within the last 7 days

## Conflict Resolution

### Documentation Conflicts
When two documents specify different values for the same parameter:
1. Check if this document (Contradiction Policy) has an authoritative value → use it
2. Check document dates — newer document's value takes precedence
3. Check scope — more specific document overrides more general
4. If still ambiguous, escalate to the architecture review board

### Priority Order (Most to Least Authoritative)
1. This document (Contradiction Policy)
2. Security policies (SEC-*)
3. Compliance requirements (COMP-*)
4. Architecture decisions (ADR-*)
5. Technology choices (TC-*)
6. Team conventions (Coding Guide, Workflow Spec)

### Known Discrepancies
The following discrepancies exist between documents and are intentional:

| Parameter | Document A (value) | Document B (value) | Resolution |
|-----------|-------------------|-------------------|------------|
| Test coverage | Coding Guide (>80%) | This doc (>90% critical) | Both correct — different scope |
| API retries | Research Protocol (3) | Coding Guide (4) | Research Protocol is authoritative for API calls; Coding Guide's "4 attempts" counts the initial attempt + 3 retries — effectively the same |
| Deploy approval | Workflow Spec (2 approvals) | Hotfix process (1 approval) | Both correct — hotfix is an expedited path |
| Data retention | Memory Decisions (90 days) | Research Protocol (2 years) | Different data types — analytics vs research |

## SLA Definitions

### Service Level Objectives
| Service | Availability | Latency P99 | Error Rate |
|---------|-------------|-------------|------------|
| Payment Gateway | 99.99% | 500ms | <0.01% |
| User Auth | 99.99% | 200ms | <0.01% |
| Order Service | 99.95% | 1000ms | <0.1% |
| Notification | 99.9% | 2000ms | <0.5% |
| Reporting | 99.5% | 5000ms | <1.0% |

### SLA Violation Response
- 1 violation in 30 days: documented, action plan created
- 2 violations in 30 days: escalated to engineering manager
- 3+ violations in 30 days: incident review, potential architecture change

## Audit Requirements

### Quarterly Audits
- API key rotation compliance check
- Test coverage trend analysis
- Exception status review (expired? renewed?)
- SLA compliance report
- Security scan results review

### Annual Audits
- Full architecture review
- Technology stack assessment
- Disaster recovery test
- Compliance certification renewal (SOC 2, GDPR)
- Team training completion verification
