# Orion AI Kit - Project Context

## Project Overview

The Orion AI Kit is a stack-agnostic environment designed to run agentic coding workflows with minimal configuration. It provides a modular, extensible framework for implementing AI-driven development processes including Planner → Retrieve/Rerank → Implementer → Critic workflows.

The project includes:
- Docker-based environment with Node.js and Python support
- AI CLI tool for stack-agnostic operations
- Memory tool for AI agents to manage persistent state
- Support for RAG (Retrieval Augmented Generation) with OpenSearch
- Integration hooks for code review processes

## Architecture

The kit follows a modular architecture where:
- **Adapters** handle different programming stacks (Node.js, Python)
- **Prompts** define the AI agent workflows (planner, implementer, critic)
- **Memory tools** provide persistent state management for AI agents
- **CLI tools** automate common development tasks
- **RAG components** enable knowledge retrieval capabilities

## Core Components

### Docker Environment
- Base image: `node:20-bookworm-slim`
- Includes: Python 3, Node.js, Git, jq, patch, and other CLI tools
- Preconfigured volumes for npm and pip caching

### AI CLI (ai_cli.py)
The main command-line interface that supports:
- `detect` - Detects project stacks (Node.js, Python)
- `run` - Executes development tasks (build, test, lint, format, coverage, mutation)
- `apply-patch` - Applies git patches
- `reports` - Generates reports for CI/CD integration

### Memory Tool
- Provides secure, path-confined file operations for AI agents
- Supports operations: view, create, replace, insert, delete, rename
- Implements security features: path traversal guard, size limits
- Default memory root: `.ai/memories`

### Prompt System
- `planner_test_plan.md` - Planning and test generation prompts
- `implementer_red.md` - Red/green implementer prompts
- `implementer_green.md` - Implementation completion prompts
- `critic.md` - Code review and critique prompts

## Building and Running

### Prerequisites
- Docker and Docker Compose
- Git

### Setup Commands
```bash
# Build the Docker environment
docker compose build

# Run detection of project stacks
docker compose run --rm ai python3 ai_cli.py detect

# Run a specific task (e.g., test)
docker compose run --rm ai python3 ai_cli.py run --task test
```

### Development Workflow
1. Place the Orion AI Kit in your target project directory
2. The CLI will automatically detect the project stack (Node.js or Python)
3. Use the CLI to run various development tasks
4. Integrate with CI/CD via the reports command

### RAG Setup (Optional)
```bash
# Start OpenSearch for RAG capabilities
docker compose -f docker-compose.rag.yml up -d
```

## Development Conventions

### Supported Stacks
- **Node.js**: Detected via `package.json`, supports npm scripts
- **Python**: Detected via `pyproject.toml` or `requirements.txt`, supports pip

### Code Quality Tools
- **Node.js**: ESLint, Prettier, Jest, Stryker for mutation testing
- **Python**: Ruff, pytest, coverage.py, mutmut for mutation testing

### Git Hooks
- Pre-PR hook runs tests, linting, and mutation testing
- Post-PR hook for post-processing tasks

### Claude Integration
- MCP (Model Context Protocol) servers enabled: GitHub, filesystem, HTTP
- Output style configured for pull requests
- Hooks for pre/post PR processes

## Security Considerations

- Memory tool implements path traversal protection
- File size limits to prevent resource exhaustion
- Sandboxed execution environment via Docker
- Path-confined operations to prevent unauthorized file access

## Extending the Kit

The kit is designed to be extensible:
- Add new stack adapters by implementing build/test/lint patterns
- Create custom prompts for specific AI workflows
- Extend the CLI with new commands
- Integrate with different RAG systems via OpenSearch
- Add custom memory handlers for different storage backends

## Project Structure

```
orion-ai-kit/
├── ai_cli.py               # Main CLI application
├── Dockerfile             # Base container configuration
├── docker-compose.yml     # Docker services definition
├── docker-compose.rag.yml # OpenSearch RAG service
├── prompts/              # AI agent prompt templates
├── memory/               # Memory tool implementation
├── scripts/              # Utility and hook scripts
├── adapters/             # Stack adapter templates
├── docs/                 # Documentation
└── .claude/settings.json # Claude Code integration settings
```