# Coding Guide — Engineering Standards

## Overview

This document defines the engineering standards, coding patterns, and testing requirements for all services in the platform. All team members must follow these guidelines.

## Topics

| Topic | File | Contents |
|-------|------|----------|
| Language and Framework Standards | → [[fundamentals.md]] | Python, TypeScript, Go standards, linting, formatting |
| Architecture Patterns | → [[patterns.md]] | Service communication, data access, circuit breaker, caching, events |
| Error Handling | → [[patterns.md]] | Error classification, retry policy, logging standards |
| Testing Standards | → [[testing.md]] | Unit, integration, e2e, performance tests, test data principles |
| Code Review and Configuration | → [[advanced.md]] | PR requirements, review criteria, config management, docs |

## Quick Reference

- Test coverage: >80% line coverage for all services
- PR size limit: 400 LOC
- Min approvals: 2 (including 1 code owner)
- Error retry policy: exponential backoff (1s, 4s, 16s)
- Circuit breaker: 3 failures → open for 30s
- Cache TTL: 5 min (changing data), 1 hour (reference data)
