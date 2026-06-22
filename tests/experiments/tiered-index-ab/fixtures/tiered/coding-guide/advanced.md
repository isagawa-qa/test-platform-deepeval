# Code Review Standards and Configuration Management

## PR Requirements
- Description template must be filled (what, why, how, testing)
- Maximum PR size: 400 lines of code changes (split larger PRs)
- Self-review before requesting others
- All CI checks must pass before review

## Review Criteria
- Correctness: does the code do what it claims?
- Clarity: can another engineer understand this in 5 minutes?
- Consistency: does it follow the patterns in this guide?
- Coverage: are edge cases handled?
- Performance: any obvious bottlenecks?

## Approval Rules
- Minimum 2 approvals required for merge
- At least 1 approval must be from a code owner for the changed files
- Author cannot self-approve
- Approvals are reset on force-push (new review required)

## Configuration Management

### Environment Variables
- Use `.env` files for local development (never committed)
- Use cloud secret manager for staging/production
- All config values must have documented defaults
- Sensitive values (API keys, passwords) must be rotated every 90 days

### Feature Flags
- Use LaunchDarkly for feature flag management
- Flag naming: `{team}.{feature}.{variant}` (e.g., `payments.new-checkout.enabled`)
- All new features behind flags in production
- Flags cleaned up within 30 days of full rollout
- Emergency kill switches for all critical paths

## Documentation Requirements

### Code Documentation
- Public functions require docstrings/JSDoc with parameter descriptions
- Complex algorithms need inline comments explaining the "why"
- Architecture Decision Records (ADRs) for significant design choices
- README.md required for every service with: purpose, setup, API summary

### API Documentation
- OpenAPI 3.0 spec required for all REST APIs
- Protobuf files serve as documentation for gRPC APIs
- Examples required for every endpoint
- Changelog maintained for API version changes
