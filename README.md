# [Project Name]

[One sentence describing what this project does.]

This repository is built with a focus on simplicity, maintainability, and strict code quality — designed to be easy to navigate for anyone reviewing the codebase.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core Architecture Dependencies](#core-architecture-dependencies)
- [Project Structure & Design Principles](#project-structure--design-principles)
- [Code Quality & CI/CD](#code-quality--cicd)

---

## Quick Start

Make sure you are inside your virtual environment, then run:

```bash
make setup    # Create data directories, install dependencies and configure pre-commit
make all      # Lint, verify, and test in one command
python src/run.py  # Run the pipeline
```

### Commands

Common tasks are available via `make` to simplify the developer experience.

```bash
make lint-fix      # Auto-fix formatting, style, and import order
make lint-verify   # Read-only checks — what CI runs
make test-unit     # Run only unit tests
make test-e2e      # Run end-to-end and non-regression tests
make test          # Run the entire test suite (unit + E2E)
make all           # lint-fix → lint-verify → test
make clean         # Remove all cache directories
make docs-serve    # Preview the documentation locally
make docs-deploy   # Deploy the documentation to GitHub Pages
```

---

## Core Architecture Dependencies

This template relies on two lightweight internal libraries:

- [dataconf-manager](https://github.com/MaximeRighini/dataconf-manager) — multi-layer YAML config merging with dynamic anchor resolution, and local file I/O for Polars DataFrames.
- [pipeline-orchestrator](https://github.com/MaximeRighini/pipeline-orchestrator) — executes ordered `Node` sequences, injects config, and handles automatic data loading and dumping based on paths defined in `config/general/general.yaml`.

Both are optional. For projects that do not need multi-environment config or formal pipeline tracing, remove them from `pyproject.toml` and delete `config/`, `src/nodes/`, and `src/pipelines/`. See the comments in `pyproject.toml` for the deps to add back manually.

---

## Project Structure & Design Principles

Each file has one job.

```text
├── config/
│   └── general/
│       └── general.yaml  # Base config defaults and data paths
├── Makefile              # Central command interface (local & CI)
├── pyproject.toml        # Single-source dependency and tool configuration
├── src/
│   ├── constants.py      # Soft-coded column names and field mappings
│   ├── utils.py          # Shared, atomic helper functions
│   ├── modules/          # Domain-driven processing logic
│   ├── nodes/            # Atomic execution units wrapping business logic
│   ├── pipelines/        # Ordered node sequences with auto I/O resolution
│   └── run.py            # Pipeline entry point
└── tests/                # Pytest test suite mirroring the src/ structure
```

**`constants.py`** centralizes every column name and field mapping. If an upstream field is renamed, one line change propagates across the entire codebase.

**`config/general/general.yaml`** holds both application settings and data paths. Keys defined under `data` are intercepted by the Pipeline engine to trigger automatic loading and dumping of Polars DataFrames. Dynamic placeholders (e.g. `{market}`, `{env}`) are resolved at runtime by `ConfigManager`.

**`nodes/`** contains atomic functions wrapped in `Node` objects. Each node handles no I/O — it receives its inputs from the pipeline context and returns a dict of outputs. Input keys are inferred automatically from the function signature.

**`pipelines/`** contains ordered sequences of nodes. The pipeline injects config, resolves inputs (from context or disk), merges outputs back into the shared context, and auto-dumps results when a data path is configured.

---

## Code Quality & CI/CD

This codebase enforces code quality at three stages of development.

1. **`make lint-verify`** runs Ruff and Mypy in read-only mode. Run it regularly during development to catch linting and type errors before they accumulate.

2. **Pre-commit hooks** act as a safety net on every commit, ensuring broken or badly formatted code never reaches the remote repository.

3. **GitHub Actions** triggers automatically on every push. It runs the same environment and the same checks as local development, so there are no surprises. Any pull request that fails linting or tests is blocked from being merged.
