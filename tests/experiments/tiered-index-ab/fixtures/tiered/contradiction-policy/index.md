# Contradiction Policy — Quality Standards and Exception Handling

## Overview

This document defines quality standards, coverage requirements, and exception handling policies. It serves as the authoritative source for thresholds and standards that may appear (sometimes with different values) in other documentation.

## Topics

| Topic | File | Contents |
|-------|------|----------|
| Coverage Standards and Exceptions | → [[coverage-standards.md]] | Test coverage thresholds (80% base, 90% critical), approved exceptions, exception process |
| Quality Gates and Conflict Resolution | → [[quality-gates.md]] | Environment gates, documentation priority order, known discrepancies, SLAs, audits |

## Quick Reference

- Baseline coverage: >80% (all services)
- Critical service coverage: >90% line + branch
- Critical services: payment-gateway, user-auth, order-service, billing-service
- Known discrepancy: Coding Guide says >80%, this doc says >90% for critical (both correct, different scope)
- Priority order: This doc > Security > Compliance > Architecture > Tech choices > Team conventions
