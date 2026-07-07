.PHONY: sync format lint test check deploy-check docs-serve docs-build

export UV_CACHE_DIR := .uv-cache

PYTHON_PATHS := apps __PROJECT_PACKAGE__ celery_app tests manage.py
MARKDOWN_PATHS := README.md README.en.md agent-docs docs skill

sync:
	uv sync --all-groups --locked

format:
	uv run --no-sync ruff format $(PYTHON_PATHS)
	uv run --no-sync ruff check --fix $(PYTHON_PATHS)
	uv run --no-sync mdformat $(MARKDOWN_PATHS)

lint:
	uv run --no-sync ruff check $(PYTHON_PATHS)
	uv run --no-sync ruff format --check $(PYTHON_PATHS)
	uv run --no-sync mypy $(PYTHON_PATHS)
	uv run --no-sync mdformat --check $(MARKDOWN_PATHS)
	uv run --no-sync python manage.py check

test:
	uv run --no-sync pytest

check: lint test

deploy-check:
	uv run --no-sync python scripts/check_deploy_env.py

docs-serve:
	uv run --no-sync mkdocs serve --dev-addr 127.0.0.1:8001

docs-build:
	uv run --no-sync mkdocs build --strict
