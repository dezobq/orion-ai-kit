#!/usr/bin/env bash
set -euo pipefail
echo "[post-pr] Collecting and listing reports..."
python3 ai_cli.py reports
