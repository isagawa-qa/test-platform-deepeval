# Compliance Decisions

## COMP-001: GDPR Deletion Requirements
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

## COMP-002: Data Pseudonymization
**Date:** 2024-02-15
**Status:** Accepted
**Decision:** Raw analytics data pseudonymized after 90 days (user ID replaced with hash). Pseudonymization mapping stored in Vault with restricted access (only data engineering team lead can access).

## COMP-003: Data Processing Agreements
**Date:** 2024-01-15
**Status:** Accepted
**Decision:** All third-party data providers must sign a Data Processing Agreement (DPA) before any data exchange. DPAs reviewed annually.
