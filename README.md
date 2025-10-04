# AI Starter Kit (Stack-Agnostic, Zero/Low-Config)

This kit gives you a minimal, **stack-agnostic** environment to run agentic coding workflows (Planner → Retrieve/Rerank → Implementer → Critic) with **Node+Python adapters** to start. It’s designed to be simple and extensible.

## Contents
- `docker-compose.yml` — one service: `ai` (runs inside a container with toolchains)
- `Dockerfile` — base image with Node LTS + Python 3 + common CLI tools
- `ai_cli.py` — one CLI for all stacks (`detect`, `run`, `apply-patch`, `reports`)
- `adapters/` — per-stack logic (future); Node+Python built-in for now
- `scripts/ai_pre_pr.sh` / `scripts/ai_post_pr.sh` — CI hooks
- `.github/workflows/ai.yml` — CI workflow
- `.claude/settings.json` — Claude Code settings template (MCP + hooks)
- `.ai/stack.json.sample` — optional config if you want to pin adapters/thresholds
- `prompts/` — prompt templates (Planner/Implementer/Critic)
- `memory/` — **Claude Memory Tool** handler + example
- `docker-compose.rag.yml` + `scripts/ingest_to_opensearch.py` — optional OpenSearch for RAG

## Quick start
```bash
docker compose build
docker compose run --rm ai python ai_cli.py detect
docker compose run --rm ai python ai_cli.py run --task test
```

## Memory Tool (Claude) — optional but recommended
- Enable with beta header `context-management-2025-06-27` and include tool:
  ```json
  { "type": "memory_20250818", "name": "memory" }
  ```
- Client-side handler lives in `memory/memory_tool.py` (safe, path-confined).
- Default memory root: `.ai/memories` (NOT committed). Create it or let the handler create it.
- Example SDK wiring: `memory/example_handler.py`.

Security: path traversal guard, size limits, and refusal to write oversize files.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
