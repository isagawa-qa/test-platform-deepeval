# Memory Decisions — Architecture Decision Log

## Overview

This document records all significant architecture and technology decisions. Each decision includes context, options considered, rationale, and consequences.

## Topics

| Topic | File | Contents |
|-------|------|----------|
| Architecture Decisions | → [[architecture-decisions.md]] | ADR-001 (Event Sourcing), ADR-002 (Microservices), ADR-003 (Repository Pattern) |
| Technology Choices | → [[technology-choices.md]] | TC-001 (PostgreSQL), TC-002 (Redis), TC-003 (GraphQL rejected), TC-004 (Kafka) |
| Data Lifecycle | → [[data-lifecycle.md]] | DL-001 (Analytics retention: 90 days raw, 2 years aggregate), DL-002 (Research), DL-003 (Logs) |
| Security Decisions | → [[security-decisions.md]] | SEC-001 (API key rotation: 90 day mandate), SEC-002 (Vault), SEC-003 (mTLS) |
| Compliance | → [[compliance.md]] | COMP-001 (GDPR deletion: 30 days), COMP-002 (Pseudonymization), COMP-003 (DPAs) |

## Quick Reference

- Event sourcing: used for order service (complex state + audit trail)
- PostgreSQL over MongoDB: relational data, ACID, team expertise
- GraphQL: rejected for internal APIs, accepted for public API
- Analytics retention: 90 days raw → daily aggregates for 2 years
- API key rotation: 90 days, auto-revoke at 120 days
- GDPR deletion: within 30 days of request
