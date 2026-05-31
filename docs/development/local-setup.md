---
doc_id: "3.7"
title: "local setup"
section: "Development"
summary: "Detailed local development setup. All Make/Task targets documented with expected behavior (§10.1)."
updated: "2026-05-17"
---

# 3.7 — local setup

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/development/README.md, README.md -->

**Purpose:** Detailed local development setup. All Make/Task targets documented with expected behavior (§10.1).

## 3.7.1 Overview

Detailed local development setup. All Make/Task targets documented with expected behavior (§10.1). See [AGENTS.md](../../AGENTS.md) for validation commands.

## 3.7.2 Environment

1. **Python:** 3.12+ (`python --version`).
2. **Virtual env:** One-shot bootstrap: `./setup.sh` (creates `.venv`, installs from `requirements.lock` when present then `pip install -e . --no-deps`, else `pip install -e ".[dev]"`, copies `.env` from `.env.example`, runs `make migrate`, lint, fmt, typecheck, test).
3. **Environment file:** Copy `cp .env.example .env` and set `JWT_SECRET_KEY` to a strong value before any shared or production use. All settings are read through `apps/api/app/config.py` only.

## 3.7.3 Running the API

- **Development server:** `make dev` (reloads on change; binds per `API_HOST` / `API_PORT` in `.env`).
- **Health checks:** `make health-check` (or `make health:check`) — exercises `/health`, `/ready`, `/live`.

## 3.7.4 Canonical Make targets

Run `make help` for the full list. Common targets:

| Target | Role |
|--------|------|
| `make lint` | Ruff lint |
| `make fmt` | Apply Ruff formatting |
| `make fmt-check` / `make fmt:check` | Ruff format verify (CI mode) |
| `make fmt-fix` / `make fmt:fix` | Alias for `make fmt` |
| `make typecheck` | mypy strict |
| `make test` | Pytest with coverage |
| `make test-unit` / `make test:unit` | Unit tests only |
| `make migrate` | Alembic upgrade to head |
| `make ci-migrate-dry-run` | Same SQLite migration checks as CI (`migrate-dry-run` job) — run before pushing migrations |
| `make migrate:create MESSAGE="..."` / `make migrate:create` | New revision (MESSAGE required) |
| `make docker-up` / `make docker:up` | `docker compose up -d` |
| `make docker-down` / `make docker:down` | `docker compose down` |
| `make skills-list` / `make skills:list` | List skills by category |
| `make queue-top-item` / `make queue:top-item` | First open row as **one JSON line** (all columns — for agents) |
| `make queue-peek` / `make queue:peek` | Raw CSV: header + first row |
| `make queue-pr-merge` / `make queue:pr-merge` | After archive+validate — merge PR (`gh pr merge --merge --delete-branch`; optional `PR_NUMBER=`) |
| `make queue-validate` / `make queue:validate` | Validate `queue/queue.csv` |
| `make audit-self` / `make audit:self` | Repo self-audit |
| `make docs-generate` / `make docs:generate` | Manual human/AI-agent generated-doc refresh; not run by CI |
| `make security-scan` / `make security:scan` | Bandit + pip-audit |
| `make secret-scan` / `make secret:scan` | Heuristic secret-pattern scan |
| `make env-sync` / `make env:sync` | Compare `.env.example` with `Settings` fields |
| `make test-scaffold MODULE=…` / `make test:scaffold` | Print pytest stubs for a router |
| `make coverage-ratchet` / `make coverage:ratchet` | Compare `coverage.xml` to policy floor |
| `make rule-lint` / `make rule:lint` | Lint `.cursor/rules` front matter |
| `make adr-index` / `make adr:index` | Regenerate `docs/adr/README.md` |
| `make codebase-summary` | Manual human/AI-agent refresh of `docs/generated/CODEBASE_SUMMARY.md`; not run by CI |

Colon forms (e.g. `make queue:peek`) are aliases to the hyphenated targets in the root `Makefile`.

## 3.7.5 Agent and queue tooling (no bundled repo MCP)

This template **does not** ship a stdio MCP server that wraps the queue, Make, or repo files. Agents follow root **[AGENTS.md](../../AGENTS.md)** using the **Makefile** and **scripts** only.

| Need | What to use |
|------|----------------|
| Active queue row (all columns, one JSON line) | `make queue:top-item` or `python scripts/queue_top_item.py` |
| Validate open + archive CSV | `make queue:validate` or `python scripts/queue_validate.py` |
| Queue CSV field rules and invariants | **[packages/queue_ops/AGENTS.md](../../packages/queue_ops/AGENTS.md)** and module **`packages.queue_ops`** |

**Implementation note:** `packages/queue_ops` is stdlib-only Python shared by the queue scripts and tests. Keep CSV logic there; do not duplicate column lists or validators in ad hoc scripts.

**FastAPI MCP (optional product surface):** The backend may expose MCP via **`fastapi-mcp`** at **`/mcp`** when that integration is enabled — that is **application** MCP, unrelated to editor automation. See **[add-mcp-tool.md](../procedures/add-mcp-tool.md)**.

## 3.7.6 IDE

Use your editor’s Python integration pointed at `.venv`. The repo uses Ruff and mypy; matching the versions in `pyproject.toml` avoids CI drift.

### Optional MCP servers in Cursor

You may register **your own** MCP servers (Figma, GitLab, Firebase, etc.) in Cursor — globally or in this repo’s **`.cursor/mcp.json`**. The template ships **`mcpServers: {}`** as a placeholder only; nothing in **`AGENTS.md`** requires a project MCP connection.

## 3.7.7 Windows Users

This template standardizes on Unix-like shells. Windows developers should use one of:

- **WSL 2** (Windows Subsystem for Linux) — Recommended. Full Linux environment with native Docker integration.
- **Git Bash** — Lightweight option bundled with Git for Windows. Run `./setup.sh` and all `make` targets from Git Bash.

PowerShell and `cmd.exe` are not directly supported. If you must use them, run commands through WSL (`wsl -e ./setup.sh`).

## 3.7.8 Related

- [environment-vars.md](environment-vars.md) — settings reference
- [testing-guide.md](testing-guide.md) — pytest and coverage
- [git-workflow.md](git-workflow.md) — branches and PRs
