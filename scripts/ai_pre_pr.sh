#!/usr/bin/env bash
set -euo pipefail
echo "[pre-pr] Running tests and basic checks..."
python ai_cli.py run --task test
python ai_cli.py run --task lint
python ai_cli.py run --task mutation || true
