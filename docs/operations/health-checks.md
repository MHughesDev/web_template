---
doc_id: "6.5"
title: "health checks"
section: "Operations"
summary: "Health check documentation: endpoint contracts, probe configuration, dependency checks, degraded states."
updated: "2026-04-17"
---

# 6.5 — health checks

<!-- CROSS-REFERENCES -->
<!-- - Referenced by: docs/operations/README.md -->

**Purpose:** Health check documentation: endpoint contracts, probe configuration, dependency checks, degraded states.

## 6.5.1 Overview

Health check documentation: endpoint contracts, probe configuration, dependency checks, degraded states. See [AGENTS.md](../../AGENTS.md) for validation commands.

## 6.5.2 Endpoints

### `GET /api/v1/utils/health-check/`

Trivial liveness probe — returns `true` with no auth and no I/O. Use this for
load-balancer / orchestrator liveness checks where you only need to know the
process is up and answering HTTP requests.

### `GET /api/v1/utils/health/dependencies/`

Dependency-readiness aggregator (superuser-only). Probes whichever external
dependencies this deployment actually has configured and returns a read-only
reachability report:

- **database** — always probed (`SELECT 1`)
- **smtp** — probed if `SMTP_HOST` is set (opens a connection, issues
  `EHLO`/`NOOP` only — never authenticates)
- **sentry** — probed if `SENTRY_DSN` is set (plain HTTP reachability check
  of the Sentry host — never `capture_message`, so it creates no events)
- **arbitrary HTTP URLs** — one entry per URL configured in
  `HEALTH_CHECK_URLS`

Each entry is a `DependencyStatus` object: `service`, `ok`, `detail`,
`latency_ms`. Services that aren't configured report `ok: true` with
`detail: "not configured"`. **No secret values (SMTP credentials, the
Sentry DSN's embedded key) ever appear in the response — only
host/port/reachability.**

Gated by `HEALTH_DEPENDENCIES_ENABLED` (default `true`); returns `404` when
disabled. Tune the per-probe timeout with `HEALTH_CHECK_TIMEOUT_SECONDS`.

Use this endpoint for readiness checks and operator dashboards — it does
real I/O and should not be hit at high frequency from a load balancer.

## 6.5.3 When to use which

| Need | Endpoint |
|------|----------|
| "Is the process alive and serving requests?" | `/utils/health-check/` |
| "Are the external services this deployment depends on reachable right now?" | `/utils/health/dependencies/` |
| "Verify my `.env` points at reachable services before deploying" | `make smoke-external` (see `docs/procedures/pre-deploy-checklist.md`) |
