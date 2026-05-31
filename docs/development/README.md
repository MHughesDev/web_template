---
doc_id: "3.0"
title: "Development overview"
section: "Development"
summary: "Index of developer documentation: setup, workflow, testing, and standards."
updated: "2026-05-17"
---

# 3.0 — Development overview

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/development/README.md, README.md -->

**Purpose:** Index of developer documentation: setup, workflow, testing, and standards.

## 3.0.1 Overview

Index of developer documentation: setup, workflow, testing, and standards. See [AGENTS.md](../../AGENTS.md) for validation commands.

**Agents:** Queue and validation commands are documented in **[local-setup.md](local-setup.md)** (section *Agent and queue tooling*). Shared queue CSV logic lives in **`packages/queue_ops`** (not a separate MCP binary).

## 3.0.2 Contents

| Document | Description |
|----------|-------------|
| [quickstart.md](quickstart.md) | Day-1 template rename and initialization quickstart |
| [local-setup.md](local-setup.md) | Bootstrap, Make targets, queue/agent tooling, IDE |
| [environment-vars.md](environment-vars.md) | Settings and `.env` reference |
| [git-workflow.md](git-workflow.md) | Branches and pull requests |
| [module-patterns.md](module-patterns.md) | FastAPI module layout |
| [testing-guide.md](testing-guide.md) | Pytest and coverage |
| [docs-generation.md](docs-generation.md) | Manual human/AI-agent docs generation helpers and docs checks |
| [dependency-management.md](dependency-management.md) | `pyproject.toml` and upgrades |
| [coding-standards.md](coding-standards.md) | Ruff, mypy, API conventions |
