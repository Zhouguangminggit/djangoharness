.PHONY: sync format lint test check

export UV_CACHE_DIR := .uv-cache

PYTHON_PATHS := apps base_framework celery_app tests manage.py
MARKDOWN_PATHS := README.md README.en.md agent-docs docs deploy/README.md skill

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
