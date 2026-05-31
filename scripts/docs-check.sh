#!/usr/bin/env bash
# scripts/docs-check.sh
# Verify internal markdown links, Make targets, and script references.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

errors = 0

# --- Check 1: Internal markdown links ---
print("Checking internal markdown links...")
root = Path("docs")
link_re = re.compile(r"\]\(([^)]+)\)")
for md in root.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="ignore")
    for m in link_re.finditer(text):
        target = m.group(1).split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("/"):
            continue
        resolved = (md.parent / target).resolve()
        try:
            resolved.relative_to(Path(".").resolve())
        except ValueError:
            continue
        if not resolved.exists():
            print(f"Broken link in {md}: {target}", file=sys.stderr)
            errors += 1

# --- Check 2: Make targets referenced in docs must exist ---
print("Checking Make targets referenced in docs...")
make_re = re.compile(r"`?make\s+([\w\-:]+)`?")
# Get valid targets from Makefile
try:
    make_output = subprocess.run(
        ["make", "help"],
        capture_output=True,
        text=True,
        timeout=30
    )
    # Fallback: parse Makefile directly if make help fails
    makefile_targets = set()
    if (Path("Makefile")).exists():
        makefile_text = Path("Makefile").read_text()
        # Match targets like "target:" and aliases like "target: other"
        for line in makefile_text.splitlines():
            if "##" in line and ":" in line:
                target = line.split(":")[0].strip()
                if target and not target.startswith("."):
                    makefile_targets.add(target)
            # Also match colon-style aliases
            if line.strip().endswith(":") and not line.startswith(" ") and not line.startswith("\t"):
                target = line.strip().rstrip(":").strip()
                if target and not target.startswith(".") and not target.startswith("$"):
                    makefile_targets.add(target)
except Exception as e:
    print(f"Warning: Could not parse Makefile: {e}", file=sys.stderr)
    makefile_targets = set()

for md in root.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="ignore")
    for m in make_re.finditer(text):
        target = m.group(1).strip()
        # Normalize colon-style targets
        target_normalized = target.replace(":", "-")
        # Skip if target doesn't exist in Makefile
        if target not in makefile_targets and target_normalized not in makefile_targets:
            # Check if it might be a pattern rule or variable
            if target.startswith(("$", "%", "@")):
                continue
            print(f"Unknown make target in {md}: '{target}'", file=sys.stderr)
            errors += 1

# --- Check 3: Script references must exist ---
print("Checking script references...")
script_re = re.compile(r"`?scripts/([\w\-]+\.\w+)`?")
scripts_dir = Path("scripts")
valid_scripts = {f.name for f in scripts_dir.glob("*") if f.is_file()} if scripts_dir.exists() else set()

for md in root.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="ignore")
    for m in script_re.finditer(text):
        script_name = m.group(1)
        if script_name not in valid_scripts:
            print(f"Unknown script reference in {md}: '{script_name}'", file=sys.stderr)
            errors += 1

# Also check in skills/, prompts/, and root docs
for extra_dir in ["skills", "prompts", "."]:
    extra_path = Path(extra_dir)
    if not extra_path.exists():
        continue
    for md in extra_path.rglob("*.md") if extra_path.is_dir() else [extra_path / "*.md"]:
        if not md.is_file():
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in script_re.finditer(text):
            script_name = m.group(1)
            if script_name not in valid_scripts:
                print(f"Unknown script reference in {md}: '{script_name}'", file=sys.stderr)
                errors += 1

if errors > 0:
    print(f"\n{errors} doc check error(s) found", file=sys.stderr)
    sys.exit(1)

print("Link and reference checks passed")
PY

echo "docs:check OK"
