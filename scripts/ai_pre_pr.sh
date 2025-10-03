#!/usr/bin/env bash
set -euo pipefail
echo "[pre-pr] Running tests and basic checks..."
python3 ai_cli.py run --task test
python3 ai_cli.py run --task lint
python3 ai_cli.py run --task mutation || true
