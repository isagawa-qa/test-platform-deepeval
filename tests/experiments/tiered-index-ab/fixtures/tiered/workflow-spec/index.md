# Workflow Specification — Engineering Operations

## Overview

This document defines the operational workflows for the engineering team including code review, deployment, incident response, monitoring, service onboarding, and release management.

## Topics

| Topic | File | Contents |
|-------|------|----------|
| Code Review Process | → [[review-gates.md]] | PR creation, review gates, approval rules, merge process |
| Deployment and Release | → [[deployment.md]] | Deploy prerequisites, canary, rollback, release process |
| Release Process | → [[release-process.md]] | Version strategy, release steps, hotfix process, cadence |
| Incident Response | → [[incident-response.md]] | Severity levels, response steps, communication |
| Monitoring and Alerting | → [[monitoring.md]] | Required alerts, health checks, dashboards, logs |
| Service Onboarding | → [[service-onboarding.md]] | New service requirements, configurations |
| Service Configurations | → [[service-configs.md]] | Per-service config: payment, user, notification, reporting |

## Quick Reference

- Deploy approvals: 2 (including CI green + no P0/P1 bugs)
- Canary: 10% traffic for 30 min
- Incident P1 response: 15 min
- Health check timeout: 5s (default)
- Release cadence: biweekly minor, quarterly major
