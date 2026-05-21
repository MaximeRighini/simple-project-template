.PHONY: help setup test-unit test-e2e test lint-fix lint-verify clean all

help:
	@echo "Available commands:"
	@echo "  make setup        - Install dependencies and configure pre-commit"
	@echo "  make lint-fix     - Automatically fix style, formatting, and imports"
	@echo "  make lint-verify  - Run all checks in read-only mode (Ruff, Mypy)"
	@echo "  make test-unit    - Run only unit tests (fast)"
	@echo "  make test-e2e     - Run end-to-end and non-regression tests"
	@echo "  make test         - Run ALL tests (unit + e2e)"
	@echo "  make all          - Fix, verify, and test"
	@echo "  make clean        - Clean cache and temporary files"
	@echo "  make docs-serve   - Preview the documentation locally"
	@echo "  make docs-deploy  - Deploy the documentation to GitHub Pages"

setup:
	@echo "Creating data directories..."
	# TODO @Maxime 2026-05-21: update with project's actual data structure
	mkdir -p data/input data/output/intermediary
	@echo "Upgrading pip..."
	python -m pip install --upgrade pip
	@echo "Installing project and dev dependencies..."
	python -m pip install -e ".[dev]"
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Setup complete! Ready to code."

lint-fix:
	@echo "Fixing style, formatting, and imports..."
	ruff check . --fix
	ruff format .

lint-verify:
	@echo "Verifying code quality (read-only)..."
	ruff check .
	ruff format --check .
	mypy src/

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/

test-e2e:
	@echo "Running E2E and non-regression tests..."
	pytest tests/e2e/

test: test-unit test-e2e
	@echo "All tests passed successfully!"

all: lint-fix lint-verify test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -name "__pycache__" -exec rm -rf {} +
	@echo "Environment cleaned."

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy
