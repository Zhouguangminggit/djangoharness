<p align="center">
  <img src="assets/product-banner.png" alt="__PRODUCT_NAME__" width="100%">
</p>

<p align="center"><strong>__PRODUCT_SUBTITLE__</strong></p>

<p align="center">
  <img alt="Python 3.10-3.13" src="https://img.shields.io/badge/Python-3.10--3.13-3776AB">
  <img alt="Django 4.2" src="https://img.shields.io/badge/Django-4.2-0C4B33">
  <img alt="Celery 5" src="https://img.shields.io/badge/Celery-5-37814A">
  <img alt="Redis 6+" src="https://img.shields.io/badge/Redis-6%2B-DC382D">
  <img alt="MySQL 8" src="https://img.shields.io/badge/MySQL-8-4479A1">
  <img alt="uv" src="https://img.shields.io/badge/deps-uv-DE5FE9">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED">
  <img alt="Quality CI" src="https://img.shields.io/badge/CI-quality_passed-2088FF">
  <img alt="macOS" src="https://img.shields.io/badge/macOS-supported-000000">
  <img alt="Windows" src="https://img.shields.io/badge/Windows-supported-0078D4">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-blue">
</p>

[中文](README.md) | English

# __PRODUCT_NAME__

__PRODUCT_NAME__ is built on the DjangoHarness engineering conventions and is
maintained by __AUTHOR_NAME__.

## Quick start

Requirements: Python 3.10 through 3.13 and uv. Production uses MySQL 8.x and Redis
6+; local development defaults to SQLite, and Redis is only required when running a
Celery worker. Dependencies use the Tsinghua PyPI mirror by default.

```bash
# Install uv if needed
python -m pip install uv

# Install and select a supported Python (3.10, 3.11, 3.12, or 3.13)
uv python install 3.10
uv python pin 3.10

# Install runtime and development dependencies from the lockfile
uv sync --all-groups --locked

# Prepare configuration and database
cp .env.example .env
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Django Admin is available at <http://127.0.0.1:8000/admin/>.

## Use the project Skill with Codex or Claude Code

The [`skill/`](skill/) directory packages the DjangoHarness agent rules as a complete project Skill. To use it with Codex or Claude Code:

1. Download or clone this repository.
1. Upload the complete `skill/` directory to the relevant project, conversation, or Skill import location in Codex or Claude Code.
1. Preserve the directory structure. Upload `SKILL.md`, `references/`, `agents/`, and `assets/` together instead of uploading only `SKILL.md`.
1. Ask the AI tool to load the DjangoHarness Skill before it creates or changes business code.

The Skill provides project structure, Django development, asynchronous task, database, and engineering quality rules. Skill import entry points may differ between tool versions; use the current interface provided by the relevant client.

## Development commands

```bash
make format  # Fix and format Python and Markdown
make lint    # Ruff, mypy, mdformat, and Django system checks
make test    # pytest
make check   # lint + test
```

## Documentation

- [Agent development rules](agent-docs/AGENTS.md)
- [macOS setup (Chinese)](docs/macos/README.md)
- [Windows setup (Chinese)](docs/windows/README.md)
- [Celery guide (Chinese)](docs/celery/README.md)
- [Deployment guide (Chinese)](docs/deploy.md)
- [Tooling guide (Chinese)](docs/makefile/README.md)
- [Production settings (Chinese)](docs/deploy.md)

## Contributing

Fork the repository and create a focused branch from the latest main branch. Read the agent rules before editing and run `make check` before submitting. Model changes must include both a migration and matching `db/*.sql`; describe behavior and verification in the pull request.

## Contact and community

For project usage, environment setup, tool installation, or deployment questions,
contact __AUTHOR_NAME__.

<table align="center">
  <tr>
    <th>Author WeChat</th>
    <th>Community group</th>
  </tr>
  <tr>
    <td align="center"><img src="assets/author.jpg" alt="Author WeChat QR code" width="280"></td>
    <td align="center"><img src="assets/group.jpg" alt="Community group QR code" width="280"></td>
  </tr>
</table>

## License

This project is available under the [MIT License](LICENSE).
