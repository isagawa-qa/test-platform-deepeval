# Memory Decisions — Architecture Decision Log

## Overview

This document records all significant architecture and technology decisions made by the engineering team. Each decision includes the context, options considered, decision rationale, and consequences. Decisions are organized by domain: architecture, technology choices, data lifecycle, security, and compliance.

## Architecture Decisions

### ADR-001: Event Sourcing for Order Service
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

### ADR-002: Microservices Over Monolith
**Date:** 2023-09-01
**Status:** Accepted
**Context:** The platform was growing beyond what a single monolith could maintain. Team size reached 15 engineers across 4 squads. Deployment cycle was 2 weeks due to merge conflicts and shared database schema changes.

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

### ADR-003: Repository Pattern for Data Access
**Date:** 2023-10-15
**Status:** Accepted
**Context:** Multiple services were writing raw SQL queries inline, making it difficult to test data access logic and swap database implementations.

**Decision:** Repository pattern with Unit of Work

**Rationale:**
- Testability: repositories can be mocked in unit tests
- Separation of concerns: business logic doesn't know about SQL
- Consistency: all data access follows the same pattern
- Migration: easier to change database technology (e.g., PostgreSQL → CockroachDB)

## Technology Choices

### TC-001: PostgreSQL Over MongoDB for User Profile Service
**Date:** 2024-02-01
**Status:** Accepted
**Context:** Choosing a database for the user profile service. Profiles include personal info, addresses (1-3 per user), preferences (key-value pairs), and notification settings.

**Options Considered:**
1. **PostgreSQL** — Relational, ACID, strong ecosystem
2. **MongoDB** — Document-oriented, flexible schema, horizontal scaling
3. **DynamoDB** — Managed NoSQL, excellent scaling, limited query flexibility

**Decision:** PostgreSQL

**Rationale:**
- User profiles have relational data: user → addresses (1:N), user → preferences (1:N)
- ACID transactions needed for profile updates that span multiple tables (e.g., update address + recalculate shipping zone)
- Team has stronger PostgreSQL expertise (3 DBAs, extensive playbooks)
- MongoDB's schema flexibility wasn't needed — the profile schema is well-defined and stable
- PostgreSQL JSONB column handles the semi-structured preferences data adequately

**When MongoDB would be preferred:**
- Document-heavy workloads without relational joins
- Rapidly evolving schemas where migrations are expensive
- Write-heavy workloads needing horizontal scaling beyond PostgreSQL's limits

### TC-002: Redis for Caching
**Date:** 2023-11-01
**Status:** Accepted
**Context:** Application-level caching needed across all services.

**Decision:** Redis with cache-aside pattern

**Rationale:**
- Sub-millisecond reads for hot data
- Pub/sub for cache invalidation across instances
- Rich data structures (sorted sets for leaderboards, lists for queues)
- Team expertise and operational tooling already in place

### TC-003: GraphQL Rejected for Internal APIs
**Date:** 2024-03-01
**Status:** Rejected (for internal APIs), Accepted (for public API)
**Context:** A team member proposed using GraphQL for all APIs to unify the query interface.

**Options Considered:**
1. **REST for all APIs** — Simple, well-understood, cacheable
2. **GraphQL for all APIs** — Flexible queries, single endpoint, typed schema
3. **REST for internal, GraphQL for public** — Best of both worlds

**Decision:** REST for internal APIs, GraphQL for public-facing API only

**Rationale for rejecting GraphQL internally:**
- Internal services have well-defined, stable contracts — REST is simpler
- GraphQL's query flexibility adds complexity without benefit for service-to-service calls
- Caching is harder with GraphQL — no HTTP cache headers on POST requests
- Monitoring and rate limiting are more complex with GraphQL (single endpoint, variable query cost)
- N+1 query problems require dataloader patterns, adding implementation complexity

**Rationale for accepting GraphQL for public API:**
- Public clients (mobile, web) have diverse data needs — GraphQL reduces over/under-fetching
- Schema serves as documentation and contract
- Client teams can evolve their queries without backend changes

### TC-004: Kafka for Event Streaming
**Date:** 2023-12-01
**Status:** Accepted
**Context:** Async event-driven communication needed between services.

**Decision:** Apache Kafka with Avro schemas

**Rationale:**
- Proven at scale (millions of events/second)
- Durable event log (replay capability)
- Consumer groups for parallel processing
- Schema Registry for contract enforcement

## Data Lifecycle

### DL-001: User Analytics Event Retention
**Date:** 2024-01-20
**Status:** Accepted
**Context:** Determining how long to keep raw user analytics events (clicks, page views, feature usage) before aggregation.

**Decision:**
- **Raw events retained for 90 days**
- After 90 days, events are aggregated into daily summaries
- **Daily summaries retained for 2 years**
- After 2 years, daily summaries are archived to cold storage (5-year retention)

**Rationale:**
- 90 days of raw data sufficient for most investigations and A/B test analysis
- Daily aggregates support trend analysis and reporting for 2 years
- Cold storage for long-term compliance (SOX requires 7-year data availability)
- Balance between storage cost and data availability

### DL-002: Research Data Retention
**Date:** 2024-02-15
**Status:** Accepted
**Decision:** Raw research data retained for 2 years, then purged

### DL-003: Log Retention
**Date:** 2024-01-10
**Status:** Accepted
**Decision:** 30 days hot, 90 days warm, 1 year cold

## Security Decisions

### SEC-001: API Key Rotation Policy
**Date:** 2024-03-15
**Status:** Accepted
**Context:** Several external-facing services use API keys for authentication. Keys had been static since creation, posing a security risk.

**Decision:**
- **90-day rotation mandate** for all external-facing API keys
- Keys older than 90 days trigger a warning alert to the service owner
- Keys older than 120 days are **automatically revoked**
- Grace period: 30 days of warnings before auto-revocation

**Implementation Status:**
- Payment service: ✅ Implemented (automated rotation via Vault)
- User service: ✅ Implemented (automated rotation via Vault)
- Notification service: ✅ Implemented (manual rotation, automated tracking)
- **Legacy reporting service: ❌ Still uses static keys** — documented exception, remediation planned for Q3 2024
  - Risk mitigation: reporting service is internal-only, not exposed to internet
  - Remediation: migrate to Vault-managed keys during Q3 infrastructure sprint

### SEC-002: Secrets Management
**Date:** 2023-11-15
**Status:** Accepted
**Decision:** HashiCorp Vault for all secrets management

### SEC-003: mTLS for Internal Services
**Date:** 2024-04-01
**Status:** Accepted
**Decision:** Mutual TLS via service mesh (Istio) for all internal gRPC traffic

## Compliance Decisions

### COMP-001: GDPR Deletion Requirements
**Date:** 2024-02-01
**Status:** Accepted
**Context:** Under GDPR, users can request deletion of their personal data. We need a process that handles deletion across all services while maintaining aggregate data for business analytics.

**Decision:**
- **Deletion requests processed within 30 days** of receipt
- Raw events for the requesting user are purged from all stores (analytics, logs, databases)
- **Daily aggregates are exempt if fully anonymized** — no user ID linkage in aggregate data
- Aggregate data without user identifiers is retained per normal retention policy
- Deletion request and completion timestamp logged for audit purposes
- Pseudonymized data treated as personal data (can be linked back) — must be deleted

**Implementation:**
- Deletion service receives request → fans out to all data stores
- Each store confirms deletion within 7 days
- Deletion service tracks completion across all stores
- Audit log records: request timestamp, completion timestamp per store, final confirmation

### COMP-002: Data Pseudonymization
**Date:** 2024-02-15
**Status:** Accepted
**Decision:** Raw analytics data pseudonymized after 90 days (user ID replaced with hash). Pseudonymization mapping stored in Vault with restricted access (only data engineering team lead can access).

### COMP-003: Data Processing Agreements
**Date:** 2024-01-15
**Status:** Accepted
**Decision:** All third-party data providers must sign a Data Processing Agreement (DPA) before any data exchange. DPAs reviewed annually.
