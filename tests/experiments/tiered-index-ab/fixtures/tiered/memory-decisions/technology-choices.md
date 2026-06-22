# Technology Choices

## TC-001: PostgreSQL Over MongoDB for User Profile Service
**Date:** 2024-02-01
**Status:** Accepted

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

## TC-002: Redis for Caching
**Date:** 2023-11-01
**Status:** Accepted
**Decision:** Redis with cache-aside pattern

**Rationale:**
- Sub-millisecond reads for hot data
- Pub/sub for cache invalidation across instances
- Rich data structures (sorted sets for leaderboards, lists for queues)
- Team expertise and operational tooling already in place

## TC-003: GraphQL Rejected for Internal APIs
**Date:** 2024-03-01
**Status:** Rejected (for internal APIs), Accepted (for public API)

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

## TC-004: Kafka for Event Streaming
**Date:** 2023-12-01
**Status:** Accepted
**Decision:** Apache Kafka with Avro schemas

**Rationale:**
- Proven at scale (millions of events/second)
- Durable event log (replay capability)
- Consumer groups for parallel processing
- Schema Registry for contract enforcement
