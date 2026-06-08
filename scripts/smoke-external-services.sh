#!/usr/bin/env bash
# scripts/smoke-external-services.sh
# Read-only connectivity smoke test for configured external services (DB/SMTP/Sentry).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT}/apps/api"
cd "${ROOT}/apps/api"
exec python3 "$ROOT/scripts/smoke_external_services.py"
