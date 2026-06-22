# Service Onboarding

## New Service Requirements
Before a new service can receive production traffic, it must complete ALL of the following:

1. **Register in service catalog** — name, team, on-call rotation, documentation link
2. **Set up CI/CD pipeline** — must pass the team's pipeline template validation
3. **Configure monitoring:**
   - Error rate alerting (threshold: >1% over 5 min)
   - Latency P99 alerting (threshold: >2s)
   - Throughput alerting (sudden drop >50%)
4. **Set up logging:**
   - Structured JSON format
   - Correlation IDs propagated
   - Log levels configured (no DEBUG in production)
5. **Create runbook:**
   - Common failure modes and remediation steps
   - Dependency list with contact info
   - Scaling procedures
6. **Load test in staging:**
   - Must handle 2x expected peak traffic
   - No errors at 1x peak
   - Latency within SLA at 1.5x peak
7. **Security review:**
   - Dependency scan (no critical CVEs)
   - Auth configuration verified
   - Input validation on all external endpoints
8. **Architecture review approval** — from the architecture review board
9. **Deploy to staging** — run integration tests, verify monitoring
10. **Canary deployment to production** — 10% traffic, 30 min observation
