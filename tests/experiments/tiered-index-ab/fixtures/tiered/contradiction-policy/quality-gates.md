# Quality Gates and Conflict Resolution

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
