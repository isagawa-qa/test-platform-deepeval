# Data Lifecycle Decisions

## DL-001: User Analytics Event Retention
**Date:** 2024-01-20
**Status:** Accepted

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

## DL-002: Research Data Retention
**Date:** 2024-02-15
**Status:** Accepted
**Decision:** Raw research data retained for 2 years, then purged

## DL-003: Log Retention
**Date:** 2024-01-10
**Status:** Accepted
**Decision:** 30 days hot, 90 days warm, 1 year cold
