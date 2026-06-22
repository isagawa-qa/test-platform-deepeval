# Architecture Decisions

## ADR-001: Event Sourcing for Order Service
**Date:** 2024-01-15
**Status:** Accepted
**Context:** The order service handles complex state transitions (created → confirmed → shipped → delivered → returned). We need a reliable audit trail for financial compliance and the ability to replay events for debugging production issues.

**Options Considered:**
1. **Traditional CRUD with audit log** — Simple but audit log can drift from actual state
2. **Event sourcing** — Events are the source of truth, state derived from replay
3. **CQRS without event sourcing** — Separate read/write models without event replay

**Decision:** Event sourcing with CQRS

**Rationale:**
- Orders have complex state transitions that benefit from event replay
- Financial audit trail is legally required (SOX compliance) — event log IS the audit trail
- Debugging production issues is dramatically easier when you can replay the exact sequence
- CQRS separation allows optimized read models for different consumers

**Consequences:**
- Higher operational complexity (event store, projections, eventual consistency)
- Team needs training on event sourcing patterns
- Event schema versioning becomes critical (use Avro with Schema Registry)
- Should only be used when audit trail or state replay benefits are required — NOT for simple CRUD services

## ADR-002: Microservices Over Monolith
**Date:** 2023-09-01
**Status:** Accepted
**Context:** The platform was growing beyond what a single monolith could maintain. Team size reached 15 engineers across 4 squads.

**Decision:** Decompose into microservices along business domain boundaries

**Rationale:**
- Independent deployment per squad (no more merge conflicts blocking releases)
- Scaling: services can scale independently based on load
- Technology diversity: teams can choose the best tool for their domain
- Fault isolation: one service failure doesn't take down the entire platform

**Consequences:**
- Network complexity increases (service mesh needed)
- Distributed tracing required for debugging
- Data consistency across services requires careful design (saga pattern)
- Operational overhead: more services to monitor, deploy, and maintain

## ADR-003: Repository Pattern for Data Access
**Date:** 2023-10-15
**Status:** Accepted

**Decision:** Repository pattern with Unit of Work

**Rationale:**
- Testability: repositories can be mocked in unit tests
- Separation of concerns: business logic doesn't know about SQL
- Consistency: all data access follows the same pattern
- Migration: easier to change database technology (e.g., PostgreSQL → CockroachDB)
