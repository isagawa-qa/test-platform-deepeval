# Code Review Process

## PR Creation
1. Create feature branch from `main` (naming: `feat/{ticket-id}-{description}`)
2. Write code, commit with conventional commits (`feat:`, `fix:`, `chore:`)
3. Self-review: run linter and tests locally before pushing
4. Create PR using the team's PR template
5. Fill all template sections: What, Why, How, Testing, Rollback Plan

## PR Template
```markdown
## What
[One sentence describing the change]

## Why
[Business context or technical motivation]

## How
[Brief technical approach]

## Testing
[What tests were added/modified, how to verify manually]

## Rollback Plan
[How to revert if something goes wrong]
```

## Review Gates
PRs must satisfy ALL of the following before merge:

1. **CI checks green** — all linting, type checking, and tests pass
2. **Minimum 2 peer approvals** — at least 1 from a code owner
3. **No unresolved comments** — all review threads must be resolved
4. **PR size < 400 LOC** — larger PRs must be split (exceptions require tech lead approval)
5. **Description complete** — all template sections filled

## Review Timeline
- First review response: within 4 business hours
- Complete review: within 1 business day
- Urgent PRs (P0 fixes): within 2 hours, minimum 1 approval sufficient

## Merge Process
1. Squash commits to clean history (one commit per PR)
2. Merge via merge queue (not direct merge to `main`)
3. Delete feature branch after merge
4. Verify deployment to staging within 30 minutes

## Approval Rules
- Minimum 2 approvals required for merge
- At least 1 approval must be from a code owner for the changed files
- Author cannot self-approve
- Approvals are reset on force-push (new review required)
