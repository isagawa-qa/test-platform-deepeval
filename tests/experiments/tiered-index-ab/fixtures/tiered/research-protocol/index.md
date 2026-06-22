# Research Protocol — Data Collection and Analysis Standards

## Overview

This document defines the standards for all research activities including data collection, API usage, analysis methodology, and reporting requirements.

## Topics

| Topic | File | Contents |
|-------|------|----------|
| Data Collection and API Standards | → [[methodology.md]] | Source selection, data formats, rate limits, API integration, error handling, retry policy |
| Analysis and Reporting | → [[analysis.md]] | Statistical requirements, data cleaning, reproducibility, reporting standards, ethics |

## Quick Reference

- API retry policy: 3 retries with exponential backoff (1s, 4s, 16s)
- Rate limit: 10 requests/second per API endpoint
- Source reliability: A (official) > B (peer-reviewed) > C (community) > D (anecdotal)
- Confidence intervals: 95% CI default
- Research data retention: 2 years
