# Security Decisions

## SEC-001: API Key Rotation Policy
**Date:** 2024-03-15
**Status:** Accepted
**Context:** Several external-facing services use API keys for authentication. Keys had been static since creation, posing a security risk.

**Decision:**
- **90-day rotation mandate** for all external-facing API keys
- Keys older than 90 days trigger a warning alert to the service owner
- Keys older than 120 days are **automatically revoked**
- Grace period: 30 days of warnings before auto-revocation

**Implementation Status:**
- Payment service: Implemented (automated rotation via Vault)
- User service: Implemented (automated rotation via Vault)
- Notification service: Implemented (manual rotation, automated tracking)
- **Legacy reporting service: Still uses static keys** — documented exception, remediation planned for Q3 2024
  - Risk mitigation: reporting service is internal-only, not exposed to internet
  - Remediation: migrate to Vault-managed keys during Q3 infrastructure sprint

## SEC-002: Secrets Management
**Date:** 2023-11-15
**Status:** Accepted
**Decision:** HashiCorp Vault for all secrets management

## SEC-003: mTLS for Internal Services
**Date:** 2024-04-01
**Status:** Accepted
**Decision:** Mutual TLS via service mesh (Istio) for all internal gRPC traffic
