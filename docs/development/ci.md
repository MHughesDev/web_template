---
doc_id: "3.9"
title: "ci"
section: "Development"
status: "pending-init"
summary: "CI pipeline stages, matrix, how to reproduce locally, common CI failures and fixes. Populated during initialization."
updated: "2026-05-17"
---

# Continuous Integration
<!-- populated by repo_initialize -->

## Pipeline stages

1. **Lint & Format** — Ruff checks
2. **Type Check** — mypy
3. **Test** — pytest with coverage
4. **Build** — Docker image build
5. **Security Scan** — dependency audit

## Security workflow (`.github/workflows/security.yml`)

Runs on PRs to `main`, weekly on schedule, and on demand. Two layers of
scanning, deliberately complementary rather than redundant:

| Job | Tool | Posture | Complements |
|-----|------|---------|-------------|
| `dependency-review` | GitHub dependency-review-action | advisory (`continue-on-error`) | — |
| `code-scan` | bandit + pip-audit (`make security-scan`) | blocking | — |
| `image-scan` | Trivy | blocking | — |
| `gitleaks` | gitleaks (git-history aware, `fetch-depth: 0`) | **blocking** | the local heuristic `make secret-scan` (`skills/security/secret-scanner.py`, runs as a pre-commit hook) — gitleaks is the industry-standard, history-aware backstop; the heuristic scanner is the fast local guard |
| `hadolint` | hadolint on `apps/api/Dockerfile` | **advisory** (`continue-on-error: true` until initial findings are triaged) | `skills/devops/dockerfile-linter.py` — same layering rationale as gitleaks/secret-scan |

Do not delete either heuristic local tool when these CI jobs are green —
they serve different audiences (fast local pre-commit guard vs.
comprehensive CI-time scan) and the layering is intentional.

## Matrix

| Python | Database | Profile |
|--------|----------|---------|
| 3.12 | PostgreSQL | default |
| 3.12 | SQLite | minimal |

## Reproducing locally

```bash
# Run the full CI pipeline locally
make preflight
make lint
make typecheck
make test
make security:scan
```

## Common failures

| Failure | Cause | Fix |
|---------|-------|-----|
| _[e.g., Lockfile out of date]_ | _[Dependencies changed]_ | _[Run `make lock`]_ |

_[This section is populated by `skills/init/repo_initialize.md` during repository initialization.]_
