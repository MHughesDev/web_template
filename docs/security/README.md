---
doc_id: "16.0"
title: "Security overview"
section: "Security"
summary: "Security documentation index."
updated: "2026-04-17"
---

# 16.0 — Security overview

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/security/README.md, AGENTS.md §11 (Escalation) -->

**Purpose:** Security documentation index.

## 16.0.1 Overview

Security documentation index. See [AGENTS.md](../../AGENTS.md) for validation commands.

## 16.0.2 Secret scanning — two complementary layers

- **Local / pre-commit:** `make secret-scan` (`skills/security/secret-scanner.py`)
  — fast, heuristic, blocking pre-commit guard.
- **CI:** the `gitleaks` job in `.github/workflows/security.yml` — git-history
  aware (full clone via `fetch-depth: 0`), industry-standard, blocking.

These are deliberately layered, not redundant: the local scanner catches
obvious leaks before they're committed; gitleaks is the comprehensive
backstop that also scans git history on every PR. Don't remove one in favor
of the other — see `docs/development/ci.md` for the full CI security-job
matrix (gitleaks + hadolint alongside the existing dependency/code/image
scans).
