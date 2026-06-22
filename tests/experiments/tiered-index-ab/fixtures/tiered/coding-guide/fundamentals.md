# Language and Framework Standards

## Python Services
- Python 3.11+ required for all new services
- Use `pyproject.toml` for dependency management (no `setup.py`)
- Type annotations required on all public functions
- Use `ruff` for linting (replaces flake8 + isort + black)
- Maximum line length: 100 characters
- Import ordering: stdlib → third-party → local (enforced by ruff)

## TypeScript Services
- TypeScript 5.0+ with strict mode enabled
- Use `pnpm` for package management (not npm or yarn)
- ESLint with the team's shared config (`@company/eslint-config`)
- Prettier for formatting (120 char line width)
- No `any` types — use `unknown` and narrow with type guards

## Go Services
- Go 1.21+ required
- Follow the standard project layout (`cmd/`, `internal/`, `pkg/`)
- Use `golangci-lint` with the team's config
- Error wrapping with `fmt.Errorf("context: %w", err)` — never bare returns
- Context propagation required on all public functions

## Dependency Management

### Security
- Dependabot/Renovate enabled for all repositories
- Critical security updates applied within 24 hours
- High severity updates applied within 1 week
- Dependency audit run weekly in CI
- No dependencies with known critical CVEs in production

### Version Pinning
- Lock files committed (`pnpm-lock.yaml`, `poetry.lock`, `go.sum`)
- Major version updates require integration testing
- Transitive dependency conflicts resolved immediately (no "works on my machine")
