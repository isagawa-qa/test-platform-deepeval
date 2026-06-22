# Release Management

## Version Strategy
- Semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: breaking API changes
- MINOR: new features, backward compatible
- PATCH: bug fixes only

## Release Process
1. **Create release branch** from `main`: `release/vX.Y.0`
2. **Run full CI suite** on release branch
3. **Update CHANGELOG.md** with version notes (using conventional commit messages)
4. **Get 2 peer approvals** on the release PR
5. **Merge to main**
6. **Tag the commit**: `vX.Y.0`
7. **Deploy to staging**, run smoke tests
8. **Deploy to production** with canary (10% traffic for 30 min)
9. **Full rollout** after canary passes
10. **Post-release monitoring** for 24 hours

## Hotfix Process
1. Branch from the release tag: `hotfix/vX.Y.1`
2. Fix the issue (minimal change only)
3. Get 1 approval (expedited review)
4. Merge to `main` and tag
5. Deploy directly (skip staging if P0)
6. Cherry-pick to any active release branches

## Release Cadence
- Minor releases: biweekly (every other Tuesday)
- Patch releases: as needed (within 24 hours for P0)
- Major releases: quarterly (planned, with migration guide)
