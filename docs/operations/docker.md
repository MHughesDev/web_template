---
doc_id: "6.4"
title: "docker"
section: "Operations"
summary: "Docker operations: building images, running containers, Compose profiles, troubleshooting."
updated: "2026-04-17"
---

# 6.4 — docker

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/operations/README.md -->

**Purpose:** Docker operations: building images, running containers, Compose profiles, troubleshooting.

## 6.4.1 Overview

Docker operations: building images, running containers, Compose profiles, troubleshooting. See [AGENTS.md](../../AGENTS.md) for validation commands.

## 6.4.2 Dockerfile linting

`apps/api/Dockerfile` is linted two ways, layered intentionally (see
`docs/development/ci.md` for the full security-job matrix):

- **Local:** `skills/devops/dockerfile-linter.py` — heuristic checks runnable
  without external binaries.
- **CI:** the `hadolint` job in `.github/workflows/security.yml` (config:
  `.hadolint.yaml`, currently minimal — advisory/`continue-on-error` until
  initial findings are triaged, then promoted to blocking).
