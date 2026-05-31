---
doc_id: "3.3"
title: "docs generation"
section: "Development"
summary: "How manual human/AI-agent docs helpers work, what they can generate on demand, and what CI must not rewrite."
updated: "2026-05-18"
---

# 3.3 — docs generation

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/development/README.md, README.md -->
<!-- - Helper code: skills/repo-governance/docs-generator.py -->
<!-- - Run: scripts/docs-generate.sh + scripts/docs-check.sh -->

**Purpose:** Explain the manual, human/AI-agent-invoked docs helpers that can produce files under `docs/generated/` from authoritative sources in the repo. CI may check documentation links and references, but it must not run generators that rewrite docs.

## 3.3.1 What docs-generation is

The docs pipeline is a small, deterministic helper. It reads source artifacts (the `Makefile`, `apps/api/app/core/config.py` Settings, `compose.yml`, `deploy/k8s/base/`, `.cursor/rules/`, `apps/api/app/alembic/versions/`) and writes indexes to `docs/generated/`:

| Output | Source | Purpose |
|---|---|---|
| `docs/generated/make-targets.md` | `Makefile` `## name: description` lines | Table of every Make target. |
| `docs/generated/settings-fields.md` | `apps/api/app/core/config.py` AST | Table of every Settings field with type and default. |
| `docs/generated/compose.md` | `compose.yml` | Service / image / ports / profiles table. |
| `docs/generated/k8s-base.md` | `deploy/k8s/base/` | One block per kind/name. |
| `docs/generated/cursor-rules.md` | `.cursor/rules/` | Rule index with scope and summary. |
| `docs/generated/migrations.md` | `apps/api/app/alembic/versions/` | Alembic revision history. |

The helper is driven by [`skills/repo-governance/docs-generator.py`](../../skills/repo-governance/docs-generator.py). It is invoked manually by humans or AI agents through `scripts/docs-generate.sh` / `make docs:generate`. `scripts/docs-check.sh` / `make docs:check` checks links and references only; it does not regenerate docs and does not fail on generated-doc drift.

## 3.3.2 What docs-generation is **not**

- **It is not the product-design brain.** The pipeline does not author architecture, design, API, or operations docs — those are written by a developer or by an AI agent following [`skills/init/repo_initialize.md`](../../skills/init/repo_initialize.md).
- **It does not replace `repo_initialize`.** The source of product intent is [`/IDEA.md`](../../IDEA.md). The source of initialization procedure is [`skills/init/repo_initialize.md`](../../skills/init/repo_initialize.md). The outputs of initialization are docs (under `docs/architecture/`, `docs/api/`, `docs/data/`, `docs/security/`, `docs/operations/`, `docs/testing/`) and queue rows.
- **It does not invent content.** Every file under `docs/generated/` is a deterministic projection of an existing source artifact in the repo. Re-running the generator on unchanged sources produces byte-identical output.

## 3.3.3 Commands

| Command | Role |
|---|---|
| `make docs-generate` / `make docs:generate` | Run `scripts/docs-generate.sh` — regenerate every file under `docs/generated/`. |
| `make docs-check` / `make docs:check` | Run `scripts/docs-check.sh` — check links and repository references without generating or rewriting docs. |

## 3.3.4 Workflow

1. Change source artifacts (`Makefile` targets, `Settings` fields, `compose.yml`, k8s manifests, cursor rules, alembic revisions).
2. If a human or AI agent decides generated reference docs should be refreshed, run `make docs-generate` and review the diff.
3. Commit any accepted documentation changes under `docs/generated/`.
4. Run `make docs-check` before pushing; CI uses the same link/reference check and does not run docs generation.

## 3.3.5 Extending the pipeline

Adding a new generator means:

- Implementing a new `DocTarget` in `skills/repo-governance/docs-generator.py` (each target is a single function that reads one source and returns a Markdown string).
- Listing the new target in `_default_targets` or `extra` so humans/AI agents can run it in `generate` mode when needed.
- Ensuring the output path under `docs/generated/` is reviewed and committed when a human/AI agent accepts the generated diff. Do not add CI jobs that auto-regenerate or fail solely on generated-doc drift.

Generators must be deterministic, side-effect-free, and stateless. Anything that requires judgment belongs in a skill, not the docs pipeline.

## 3.3.6 Related

- [skills/repo-governance/docs-generator.md](../../skills/repo-governance/docs-generator.md) — skill that wraps the helper.
- [skills/init/repo_initialize.md](../../skills/init/repo_initialize.md) — canonical initialization procedure; produces design docs, not generated docs.
- [docs/api/endpoints.md](../api/endpoints.md) — endpoint catalog (regenerate when routes change).
