# AI Starter Kit (Stack-Agnostic, Zero/Low-Config)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=coverage)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)
[![codecov](https://codecov.io/gh/dezobq/orion-ai-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/dezobq/orion-ai-kit)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=bugs)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=dezobq_orion-ai-kit&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=dezobq_orion-ai-kit)

This kit gives you a minimal, **stack-agnostic** environment to run agentic coding workflows (Planner → Retrieve/Rerank → Implementer → Critic) with **Node+Python adapters** to start. It's designed to be simple and extensible.

## Features

### Quality & Testing
- ✅ **100% Mutation Coverage** - Stryker mutation testing
- ✅ **100% Code Coverage** - Jest with enforced quality gates (≥80%)
- ✅ **SonarCloud Analysis** - Code quality, security, and tech debt tracking
- ✅ **Codecov Integration** - Coverage trends and PR comments
- ✅ **ESLint + Ruff** - Multi-language linting

### RAG & Code Search
- 🔍 **OpenSearch** - BM25 + KNN hybrid search (384-dim embeddings)
- 📚 **Code Ingestion** - Automatic chunking with git metadata
- 🎯 **Query Patterns** - Full-text and semantic search ready

### CI/CD Pipeline (13 Steps)
- 🐳 Docker-based builds
- 🧪 Automated testing (unit + mutation)
- 📊 Quality gates enforcement
- 📈 Coverage & metrics tracking
- 🔐 Security scanning

## Contents
- `docker-compose.yml` — AI service with toolchains (Node 20 + Python 3.11)
- `Dockerfile` — Base image with testing & analysis tools
- `ai_cli.py` — Stack-agnostic CLI (`detect`, `run`, `apply-patch`, `reports`)
- `scripts/` — Quality gates, ingestion, summaries, CI hooks
- `.github/workflows/ai.yml` — Complete CI/CD pipeline
- `prompts/` — Agent prompt templates (Planner/Implementer/Critic)
- `memory/` — Claude Memory Tool handler (path-confined, secure)
- `docker-compose.rag.yml` + `scripts/ingest_to_opensearch.py` — RAG infrastructure

## Quick Start

### 1. Run Tests & Quality Checks
```bash
docker compose build
docker compose run --rm ai python ai_cli.py detect
docker compose run --rm ai python ai_cli.py run --task test
docker compose run --rm ai python ai_cli.py run --task coverage
docker compose run --rm ai python ai_cli.py run --task mutation
```

### 2. Check Quality Gates
```bash
python scripts/check_thresholds.py --min-coverage 0.80 --min-mutation 0.60
```

### 3. Start OpenSearch for RAG
```bash
docker compose -f docker-compose.rag.yml up -d
docker compose run --rm ai python scripts/ingest_to_opensearch.py
```

### 4. Query Code
```bash
curl -X GET "http://localhost:9200/code-chunks/_search" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"content": "test"}}}'
```

## Documentation

- 📖 [CLAUDE.md](CLAUDE.md) - Comprehensive development guide
- 🔍 [docs/rag_queries.md](docs/rag_queries.md) - RAG query patterns and examples
- 🔐 [.github/SONAR_SETUP.md](.github/SONAR_SETUP.md) - SonarCloud integration guide

## Memory Tool (Claude) — Optional

Enable with beta header `context-management-2025-06-27`:
```json
{ "type": "memory_20250818", "name": "memory" }
```

- Handler: `memory/memory_tool.py` (path-confined, secure)
- Storage: `.ai/memories` (gitignored)
- Security: path traversal guard, size limits
- Example: `memory/example_handler.py`

## CI/CD Integration

### Required Secrets
- `CODECOV_TOKEN` - For private repos (public repos work automatically)
- `SONAR_TOKEN` - Get from [SonarCloud](https://sonarcloud.io)

### Pipeline Steps
1. Build → 2. Detect → 3. Test → 4. Lint → 5. Coverage
6. Mutation → 7. Quality Gates → 8. Summary → 9. Artifacts
10. Codecov → 11. Setup Java → 12. SonarCloud → 13. Reports

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Built with:** Node 20 • Python 3.11 • OpenSearch • Docker • GitHub Actions • Jest • Stryker • SonarCloud • Codecov
