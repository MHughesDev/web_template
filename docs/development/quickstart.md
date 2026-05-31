---
doc_id: "3.12"
title: "quickstart"
section: "Development"
summary: "Day-1 developer quickstart for renaming a new product repository and starting the docs-first initialization workflow."
updated: "2026-05-30"
---

# 3.12 — quickstart

**Purpose:** Short path for a new repository created from this template. For the full SOP, see [day 1 from template](../procedures/day-1-from-template.md).

## Day-1 commands

Preview and apply the product rename:

```bash
python3 scripts/rename-from-template.py acme-portal --dry-run
python3 scripts/rename-from-template.py acme-portal --system-name "Acme Portal"
```

Sweep for remaining template placeholders:

```bash
python3 scripts/template_token_sweep.py acme-portal
```

Then fill `IDEA.md` and ask an AI agent to run `skills/init/repo_initialize.md`. The initialization flow is docs-first and queue-first; it should not write product code.

## Documentation policy

Documentation updates are human-authored or AI-agent-authored changes reviewed in pull requests. CI may check links and references with `make docs:check`, but CI must not run documentation generators that rewrite repository docs.
