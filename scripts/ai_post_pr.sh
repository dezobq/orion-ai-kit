#!/usr/bin/env bash
set -euo pipefail
echo "[post-pr] Collecting and listing reports..."
python ai_cli.py reports
