# skills/repo-governance/docs-generator.md

<!-- CROSS-REFERENCES -->
<!-- - Machinery: skills/repo-governance/docs-generator.py -->
<!-- - Conceptual docs: docs/development/docs-generation.md -->
<!-- - Make targets: make docs:generate, make docs:check -->

**Purpose:** How to run, extend, and maintain the **deterministic docs-indexing pipeline**. The pipeline projects authoritative sources (Makefile help lines, Pydantic Settings AST, `compose.yml`, k8s YAML, cursor rules, Alembic versions) into stable Markdown indexes under `docs/generated/`. It is a small helper, not the product-design brain.

## Purpose

The pipeline is a deterministic indexer / scaffolder. It exists to help humans and AI agents refresh `docs/generated/` files from authoritative sources on demand. It **does not** author architecture, API, data, or operations docs — those are written by a developer or by an AI agent following [`skills/init/repo_initialize.md`](../init/repo_initialize.md).

Source-of-truth boundaries this skill respects:

- Source of **product intent** → [`/IDEA.md`](../../IDEA.md) (human-authored).
- Source of **initialization procedure** → [`skills/init/repo_initialize.md`](../init/repo_initialize.md) (canonical skill).
- Source of **deterministic index files** under `docs/generated/` → this pipeline.
- Source of **product design docs** under `docs/architecture/`, `docs/api/`, `docs/data/`, `docs/security/`, `docs/operations/`, `docs/testing/` → `repo_initialize` phase 3 and subsequent queue-row execution.

This skill never writes outside `docs/generated/`.

## When to invoke

- After any change to a source file that has a corresponding generated doc target (Makefile help lines, Settings, compose, k8s, cursor rules, alembic versions).
- To add a new source→target mapping to the pipeline.
- On release preparation (ensure all generated docs are fresh).

Do **not** invoke this skill for product documentation work. For that, see `skills/init/repo_initialize.md` (initialization) or the relevant `docs/procedures/update-documentation.md` SOP (ongoing).

## Prerequisites

- Python 3.12+ available.
- The repo's source artifacts exist where the targets expect them: `Makefile`, `apps/api/app/core/config.py`, `compose.yml`, `deploy/k8s/base/`, `.cursor/rules/`, `apps/api/app/alembic/versions/`.
- Optional: PyYAML installed for compose/k8s output (gracefully skipped otherwise).

## Relevant Files/Areas

- `skills/repo-governance/docs-generator.py` — the engine (read this before extending)
- `scripts/docs-generate.sh` → `make docs:generate`
- `scripts/docs-check.sh` → `make docs:check`
- `docs/development/docs-generation.md` — human-readable docs about the pipeline

## Step-by-Step Method — Running

Numbered steps for running the pipeline:
1. `make docs:generate` — regenerate all docs from source
2. Review changed files: `git diff docs/`
3. If expected changes: commit with `docs: regenerate from source`
4. `make docs:check` — verify links and references before handoff

## Step-by-Step Method — Extending

Numbered steps for adding a new source→target mapping:
1. Read the TARGETS list in docs-generator.py completely
2. Write a new generator function: `generate_<name>() -> str`
   - Parse the source file(s)
   - Format as token-efficient Markdown (tables preferred over prose)
   - Add source annotation comment
3. Register a new DocTarget in TARGETS with source_paths and target_path
4. Run `make docs:generate` to test the new generator
5. Run the generator twice or inspect the diff to verify it produces stable output
6. Update `docs/development/docs-generation.md` with the new mapping

## Command Examples

- `make docs:generate` — generate all docs
- `make docs:check` — check links and references without generating docs
- `python skills/repo-governance/docs-generator.py --generate` — generate only
- `python skills/repo-governance/docs-generator.py --check` — check only
- `python skills/repo-governance/docs-generator.py --generate --target env-vars` — specific target

## Validation Checklist

- [ ] make docs:generate runs without error
- [ ] make docs:check passes for links and references
- [ ] New generator produces valid Markdown
- [ ] Source annotations present in generated sections
- [ ] docs/development/docs-generation.md updated if new mapping added

## Common Failure Modes

- **App import error**: generator can't import FastAPI app → endpoint docs fail. Fix: ensure PYTHONPATH includes apps/api/app.
- **Generator produces unstable output**: timestamps or sort order varies → use deterministic formatting.

## Handoff Expectations

All accepted generated docs committed, make docs:check passes, new mapping documented.

## Related Procedures

docs/procedures/update-documentation.md, docs/development/docs-generation.md

## Related Prompts

prompts/documentation_updater.md

## Related Rules

.cursor/rules/documentation.md (doc update triggers)

## Machinery

`skills/repo-governance/docs-generator.py` — the complete generation engine. Supports --generate and --check modes. See file docstring for full API. Invoked by `scripts/docs-generate.sh`; `scripts/docs-check.sh` intentionally does not run it.
