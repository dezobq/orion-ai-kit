# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

**orion-ai-kit** is a stack-agnostic framework for agentic coding workflows (Planner → Retrieve/Rerank → Implementer → Critic). The architecture centers around:

- **Unified CLI** (`ai_cli.py`): Single entry point for all operations across different stacks
- **Stack Adapters**: Built-in support for Node.js and Python with extensible adapter pattern
- **Docker-first Development**: All operations run inside containers for consistency
- **Memory Tool Integration**: Optional Claude Memory Tool handler for persistent context (`.ai/memories/`)
- **CI/CD Hooks**: Pre-PR and post-PR scripts integrated with GitHub Actions

### Key Components

- `ai_cli.py` - Main orchestrator with stack detection and task routing
- `adapters/` - Stack-specific implementations (future extensibility)
- `prompts/` - Agent prompt templates (planner, implementer_red, implementer_green, critic)
- `memory/memory_tool.py` - Client-side Claude Memory Tool handler with path traversal protection
- `scripts/ai_pre_pr.sh` & `scripts/ai_post_pr.sh` - CI hooks
- `.claude/settings.json` - Claude Code configuration with MCP servers and hooks

## Common Commands

### Local Development

**Build:**
```bash
npm run build
# or inside Docker:
docker compose run --rm ai python ai_cli.py run --task build
```

**Test:**
```bash
npm test
# or inside Docker:
docker compose run --rm ai python ai_cli.py run --task test
```

**Lint:**
```bash
npm run lint
# or inside Docker:
docker compose run --rm ai python ai_cli.py run --task lint
```

**Coverage:**
```bash
npm run coverage
# or inside Docker:
docker compose run --rm ai python ai_cli.py run --task coverage
```

**Mutation Testing:**
```bash
npm run mutation
# or inside Docker:
docker compose run --rm ai python ai_cli.py run --task mutation
```

### Docker Workflow

```bash
# Build container
docker compose build

# Detect stacks
docker compose run --rm ai python ai_cli.py detect

# Run any task
docker compose run --rm ai python ai_cli.py run --task <build|test|lint|format|coverage|mutation>

# Apply a patch
docker compose run --rm ai python ai_cli.py apply-patch --file <path>

# List reports
docker compose run --rm ai python ai_cli.py reports
```

### Stack Detection

The `ai_cli.py` automatically detects stacks by checking for:
- Node.js: `package.json`
- Python: `pyproject.toml` or `requirements.txt`

Each adapter provides: build, test, lint, format, coverage, and mutation tasks.

## TypeScript Configuration

- Strict mode enabled with additional safety checks (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`)
- Module system: `nodenext` targeting `esnext`
- JSX support with `react-jsx`
- Source maps and declarations enabled

## CI/CD Pipeline

GitHub Actions workflow ([.github/workflows/ai.yml:1-46](.github/workflows/ai.yml#L1-L46)) runs on PR and workflow_dispatch:

1. **Build Docker image** - Builds container with all tooling
2. **Detect stacks** - Auto-detects Node.js/Python projects
3. **Run tests** - Executes unit tests with JUnit reporting
4. **Run lint** - Code quality checks (ESLint/Ruff)
5. **Run coverage** - Code coverage analysis (Cobertura/LCOV)
6. **Run mutation testing** - Stryker mutation tests (best-effort with `|| true`)
7. **Generate summary** - Creates GitHub Step Summary with metrics
8. **Upload artifacts** - Publishes reports (retention: 30 days)
9. **List reports** - Final inventory of all generated reports

### CI Hooks

**Pre-PR** ([scripts/ai_pre_pr.sh:1-7](scripts/ai_pre_pr.sh#L1-L7)):
```bash
python ai_cli.py run --task test
python ai_cli.py run --task lint
python ai_cli.py run --task mutation || true
```

**Post-PR** ([scripts/ai_post_pr.sh:1-5](scripts/ai_post_pr.sh#L1-L5)):
```bash
python ai_cli.py reports  # Lists all reports
```

### GitHub Step Summary

The pipeline generates a comprehensive summary ([scripts/generate_summary.py:1-201](scripts/generate_summary.py#L1-L201)):

- **Unit Tests**: Pass/fail status, duration, error counts
- **Code Coverage**: Line and branch coverage percentages
- **Mutation Testing**: Mutation score, killed/survived mutants
- **Artifacts**: Links to downloadable reports

Example output:
```
# 🤖 AI Pipeline - Test Results

## ✅ Unit Tests
- Total: 5 tests
- Passed: 5 ✅
- Duration: 0.92s

## 🟢 Code Coverage
- Line Coverage: 85.3%
- Branch Coverage: 78.1%

## 🟢 Mutation Testing
- Mutation Score: 100.0%
- Total Mutants: 2
- Killed: 2 💀
- Survived: 0 🧟

✅ Status: Excellent mutation coverage!
```

### Artifacts Published

All artifacts are uploaded with 30-day retention:
- `junit.xml` - Unit test results (JUnit format)
- `reports/coverage.xml` - Coverage report (Cobertura)
- `reports/lcov.info` - Coverage report (LCOV format)
- `reports/mutation/mutation.html` - Interactive mutation report
- `reports/mutation/mutation.json` - Mutation data (machine-readable)

### Enforcing Quality Gates

**✅ ACTIVE**: Quality gates are now enforced via [scripts/check_thresholds.py:1-119](scripts/check_thresholds.py#L1-L119)

The pipeline runs quality gates after mutation testing ([.github/workflows/ai.yml:27-31](.github/workflows/ai.yml#L27-L31)):
```yaml
- name: Quality gates (coverage & mutation)
  if: always()
  run: |
    docker compose run --rm --entrypoint "" ai bash -lc \
      "python3 scripts/check_thresholds.py --min-coverage 0.80 --min-mutation 0.60"
```

**Default Thresholds:**
- **Coverage**: ≥80% line coverage (fails build if below)
- **Mutation**: ≥60% mutation score (fails build if below)

**Usage:**
```bash
# Check with default thresholds (80% coverage, 60% mutation)
python scripts/check_thresholds.py

# Custom thresholds
python scripts/check_thresholds.py --min-coverage 0.85 --min-mutation 0.70

# Skip specific checks
python scripts/check_thresholds.py --skip-coverage  # mutation only
python scripts/check_thresholds.py --skip-mutation  # coverage only
```

**Example Output:**
```
📊 Quality Metrics:
  Line coverage: 100.0% (min: 80.0%)
  Mutation score: 100.0% (min: 60.0%)

✅ QUALITY GATES PASSED
```

**On Failure:**
```
📊 Quality Metrics:
  Line coverage: 75.3% (min: 80.0%)
  Mutation score: 55.1% (min: 60.0%)

❌ QUALITY GATES FAILED: coverage 75.3% < 80.0%; mutation 55.1% < 60.0%

To fix:
  - Add more unit tests to increase coverage
  - Strengthen test assertions to kill more mutants
  - Cover edge cases and error conditions
```

**Stryker Thresholds** in [stryker.conf.json:22-26](stryker.conf.json#L22-L26):
- **High**: 80% (excellent)
- **Low**: 60% (acceptable)
- **Break**: 50% (minimum to pass)

### Codecov Integration

**✅ ACTIVE**: Coverage tracking via Codecov ([.github/workflows/ai.yml:49-58](.github/workflows/ai.yml#L49-L58))

Coverage reports are automatically uploaded to Codecov after each PR:
```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: reports/cobertura-coverage.xml,reports/coverage.xml,reports/lcov.info
    flags: unittests
    fail_ci_if_error: false
```

**Setup (First Time):**
1. **Public Repos**: No setup needed - Codecov works automatically
2. **Private Repos**: Add `CODECOV_TOKEN` to GitHub Secrets:
   - Go to https://codecov.io and login with GitHub
   - Select your repository
   - Copy the upload token
   - GitHub → Settings → Secrets → Actions → New secret
   - Name: `CODECOV_TOKEN`, Value: `<your-token>`

**Features:**
- 📊 **Coverage Trends**: Track coverage over time
- 📈 **PR Comments**: Automatic coverage reports on PRs
- 🎯 **File-level Coverage**: See coverage per file
- 🔍 **Diff Coverage**: Coverage on changed lines only
- 🏆 **Badges**: Add coverage badge to README

**Configuration** ([codecov.yml:1-45](codecov.yml#L1-L45)):
- Target: 80% project coverage
- Threshold: ±2% acceptable variance
- Ignores: node_modules, dist, test files, config files
- Precision: 1 decimal place

**Add Badge to README:**
```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/orion-ai-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/orion-ai-kit)
```

## Memory Tool (Optional)

Claude Memory Tool integration via `memory/memory_tool.py`:
- Memory root: `.ai/memories/` (excluded from git)
- Path traversal protection and size limits (200K read, 500K write)
- Commands: view, create, str_replace, insert, delete, rename
- Enable with beta header `context-management-2025-06-27`

## MCP Servers

Enabled MCP servers in `.claude/settings.json`:
- `github` - GitHub integration
- `filesystem` - File operations
- `http` - HTTP requests

## Mutation Testing

Configuration in `stryker.conf.json`:
- **Current scope**: `sum.js` (demo) + `src/**/*.{js,ts}` (when available)
- **Exclusions**: Test files (`*.test.*`, `*.spec.*`), config files
- **Thresholds**: High: 80%, Low: 60%, Break: 50%
- **Reporters**: Progress, clear-text, HTML, JSON

### Best Practices

1. **Incremental Expansion**: Start with critical modules, expand gradually
2. **Strong Test Assertions**: Mutants only die if tests verify behavior properly
3. **Edge Cases**: Cover null/undefined, boundaries, negative cases
4. **CI Integration**: Run mutation tests in PRs (use `|| true` until calibrated)
5. **Score Monitoring**: Track per-file scores in HTML report, address low-scoring areas

### Scaling the Config

When adding source code to `src/`:
```json
"mutate": [
  "src/**/*.js",
  "src/**/*.ts",
  "!src/**/*.test.js",
  "!src/**/*.test.ts",
  "!**/*.config.js"
]
```

## Reports

All test and coverage reports are generated in the `reports/` directory:
- **JUnit XML**: `reports/junit.xml` or `junit.xml` (root)
- **Coverage**: `reports/coverage.xml`, `reports/cobertura-coverage.xml`
- **Mutation**: `reports/mutation/mutation.html` (interactive report), `reports/mutation/mutation.json`

## Next Steps: RAG + OpenSearch Integration

OpenSearch is configured and running. To enable code retrieval:

1. **Create Code Index**:
   ```bash
   curl -X PUT "localhost:9200/code-chunks" -H 'Content-Type: application/json' -d '{
     "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
     "mappings": {
       "properties": {
         "path": { "type": "keyword" },
         "lang": { "type": "keyword" },
         "symbol": { "type": "text" },
         "sha": { "type": "keyword" },
         "lines": { "type": "integer_range" },
         "body": { "type": "text" }
       }
     }
   }'
   ```

2. **Ingest Code**: Use `scripts/ingest_to_opensearch.py` to chunk and index source files

3. **Implement Retrieval**:
   - Hybrid search (BM25 + vector embeddings)
   - Reranker for precision
   - Integration with Planner → Retrieve → Implementer → Critic workflow
