#!/usr/bin/env bash
# scripts/doctor.sh
# Local developer environment preflight: versions, registry reachability,
# venv presence, import smoke test — then chains into scripts/preflight.sh.
#
# This is a LOCAL DIAGNOSTIC, not a CI gate: package-index reachability
# checks are *expected* to fail on network-restricted CI runners. Never
# wire this into .github/workflows/*.yml.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ERRORS=0

step() { echo ""; echo "[doctor] $1"; }
ok()   { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; ERRORS=$((ERRORS + 1)); }

# 1. Python version (>= 3.12 per apps/api/pyproject.toml requires-python)
# Prefer the project venv's interpreter — that's what `make dev`/`make test` use.
step "Python version"
DOCTOR_PYTHON="$ROOT/.venv/bin/python3"
[ -x "$DOCTOR_PYTHON" ] || DOCTOR_PYTHON="python3"
PY_VERSION="$("$DOCTOR_PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")"
PY_MAJOR="${PY_VERSION%%.*}"
PY_MINOR="${PY_VERSION##*.}"
if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 12 ]; }; then
    ok "$DOCTOR_PYTHON: $PY_VERSION (>= 3.12 required)"
else
    fail "$DOCTOR_PYTHON: $PY_VERSION found; >= 3.12 required (apps/api/pyproject.toml). Run: cd apps/api && uv sync --group dev"
fi

# 2. Node/bun toolchain (frontend)
step "Frontend toolchain (bun/node)"
if command -v bun >/dev/null 2>&1; then
    ok "bun $(bun --version)"
elif command -v node >/dev/null 2>&1; then
    ok "node $(node --version) (no bun found — apps/web expects bun, see package.json)"
else
    fail "neither bun nor node found on PATH. Install bun: https://bun.sh"
fi

# 3. Package-index reachability (lightweight, respects proxy env vars)
step "Package-index reachability"
PYPI_URL="${PIP_INDEX_URL:-https://pypi.org/simple/}"
if python3 - "$PYPI_URL" <<'PYEOF' >/dev/null 2>&1
import sys, urllib.request
url = sys.argv[1]
urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=5)
PYEOF
then
    ok "PyPI reachable ($PYPI_URL)"
else
    fail "PyPI unreachable at $PYPI_URL — check network/PIP_INDEX_URL/HTTP_PROXY/HTTPS_PROXY"
fi

NPM_URL="${NPM_CONFIG_REGISTRY:-https://registry.npmjs.org/}"
if python3 - "$NPM_URL" <<'PYEOF' >/dev/null 2>&1
import sys, urllib.request
url = sys.argv[1]
urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=5)
PYEOF
then
    ok "npm registry reachable ($NPM_URL)"
else
    fail "npm registry unreachable at $NPM_URL — check network/NPM_CONFIG_REGISTRY/HTTP_PROXY/HTTPS_PROXY"
fi

# 4. venv presence
step "Python virtual environment"
if [ -d "$ROOT/.venv" ]; then
    ok ".venv present at $ROOT/.venv"
else
    fail ".venv missing — run: cd apps/api && uv sync --group dev"
fi

# 5. Module import smoke test
step "Module import smoke test"
MISSING_MODULES=""
for mod in fastapi sqlmodel pytest ruff mypy; do
    if ! "$DOCTOR_PYTHON" -c "import $mod" >/dev/null 2>&1; then
        MISSING_MODULES="$MISSING_MODULES $mod"
    fi
done
if [ -z "$MISSING_MODULES" ]; then
    ok "fastapi, sqlmodel, pytest, ruff, mypy all importable"
else
    fail "missing modules:$MISSING_MODULES — run: cd apps/api && uv sync --group dev"
fi

# Summary + chain into preflight
echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✓ doctor: environment looks healthy — chaining into preflight"
    exec "$ROOT/scripts/preflight.sh"
else
    echo "✗ doctor: found $ERRORS issue(s) — fix the items above before continuing"
    exit 1
fi
