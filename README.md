# [Project Name]

[One sentence describing what this project does.]

This repository is built with a focus on simplicity, maintainability, and strict code quality — designed to be easy to navigate for anyone reviewing the codebase.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure & Design Principles](#project-structure--design-principles)
- [Code Quality & CI/CD](#code-quality--cicd)

---

## Quick Start

Make sure you are inside your virtual environment, then run:

```bash
make setup    # Create data directories, install dependencies and configure pre-commit
make all      # Lint, verify, and test in one command
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

## Project Structure & Design Principles

This repository follows a strict separation of concerns, keeping each component focused and easy to navigate.

```text
├── Makefile             # Central command interface (local & CI)
├── pyproject.toml       # Single-source dependency and tool configuration
├── src/
│   ├── config.py        # Environment and execution configuration
│   ├── constants.py     # Schema definitions and soft-coded string mappings
│   ├── utils/           # Shared, atomic helper functions
│   ├── modules/         # Domain-driven processing logic
│   └── run.py           # Single pipeline orchestration entry point
└── tests/               # Pytest test suite mirroring the src/ structure
```

---

## Code Quality & CI/CD

This codebase enforces code quality at three stages of development:

1. **`make lint-verify`** runs Ruff and Mypy in read-only mode. Run it regularly during development to catch linting and type errors before they accumulate.

2. **Pre-commit hooks** act as a safety net on every commit, ensuring broken or badly formatted code never reaches the remote repository.

3. **GitHub Actions** triggers automatically on every push. It runs the same environment and the same checks as local development, so there are no surprises. Any pull request that fails linting or tests is blocked from being merged.
