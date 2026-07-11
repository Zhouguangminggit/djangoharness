---
name: djangoharness-business
description: Implement, modify, review, and verify DjangoHarness business projects using Django 4.2, Python 3.10+, Celery, Redis, pytest-django, Ruff, mypy, uv, MySQL 8 reference SQL, Loguru, Unfold Admin, authentication, notifications, AI integration, templates, documentation, and iteration-record conventions. Use for DjangoHarness work involving architecture, apps, models, migrations, SQL, views, forms, URLs, templates, static assets, settings, permissions, authentication, verification codes, asynchronous tasks, Admin, logging, dependencies, tests, business documentation, refactoring, or acceptance fixes.
---

# DjangoHarness Business

Follow the project's Agent documentation while preserving existing behavior and user changes.

## Start every task

1. Locate the generated Django project root. Treat paths in the references as relative to that root.
2. Read [references/AGENTS.md](references/AGENTS.md) and
   [references/project-structure.md](references/project-structure.md).
3. Inspect the repository's current code, tests, configuration, local `AGENTS.md`, and working-tree
   changes before editing. Repository-local instructions and current implementation take precedence
   when they are newer or more specific than this bundled snapshot.
4. Load every task-specific reference listed below that applies to the requested change.
5. Before coding, trace existing models, services, routes, tests, and cross-app dependencies, then
   state the smallest coherent design, including business invariants, state transitions,
   authorization, transaction boundaries, retry safety, and post-commit side effects where relevant.

## Route by task

- New business domains, cross-app workflows, state machines, large-file decomposition, or refactors:
  read [references/architecture.md](references/architecture.md).
- Django apps, models, views, forms, URLs, templates, or static files: read
  [references/django-development.md](references/django-development.md).
- Models, schema, migrations, constraints, indexes, or `db/*.sql`: also read
  [references/database.md](references/database.md).
- Dependencies, tests, typing, linting, MkDocs, delivery checks, or Skill synchronization: read
  [references/engineering-quality.md](references/engineering-quality.md).
- Celery, Redis, retries, idempotency, or background work: read
  [references/async-tasks.md](references/async-tasks.md).
- Accounts, login, access control, profile data, or verification codes: read
  [references/authentication.md](references/authentication.md).
- Layouts, CSS, JavaScript, Crispy Forms, or template naming: read
  [references/template-and-style.md](references/template-and-style.md).
- Django Admin, Unfold, dashboards, imports, or management actions: read
  [references/admin.md](references/admin.md).
- In-app and broadcast notifications: read
  [references/notifications.md](references/notifications.md).
- Logging, request context, diagnostics, or exception handling: read
  [references/logging.md](references/logging.md).
- AI providers, generation tasks, or AI Admin workflows: read
  [references/ai-integration.md](references/ai-integration.md).
- Reusable blog or CMS behavior: read [references/blog.md](references/blog.md).

Read every applicable reference for cross-cutting work. Do not stop at the first matching route.

## Implement

- Preserve Python 3.10+ and Django 4.2 compatibility.
- Keep HTTP and Admin orchestration at delivery boundaries, validation in forms, use-case and
  transaction orchestration in services, reusable reads in QuerySets/selectors, and scheduling
  boundaries in Celery tasks.
- Call across apps only through public service or selector APIs. Do not import another app's views,
  forms, Admin, or signal handlers, and do not use signals to orchestrate core business workflows.
- Centralize state transitions in one service entry point. For contested writes, combine
  `transaction.atomic()`, appropriate row locks, database constraints, and idempotency keys.
- Schedule email, notifications, Celery tasks, and external calls with `transaction.on_commit()`
  when they depend on a successful transaction.
- Use named URLs, CSRF protection, explicit authentication and authorization, namespaced templates,
  and environment-backed secrets.
- Use `get_user_model()` or `settings.AUTH_USER_MODEL`; never import Django's built-in `User`
  directly.
- Use Loguru for new business logging and exclude credentials, verification codes, tokens, and
  private payloads.
- Mock email, Redis, Celery brokers, SDKs, and external APIs in tests. Cover success, denial,
  invalid state, duplicate/idempotent requests, rollback, and concurrency when applicable.
- Paginate list views, prefetch template-facing relations, and add query-count assertions for
  important list, dashboard, and context-processor paths.
- For each model change, create a Django migration and synchronize the matching MySQL 8 reference
  file under `db/`. Treat migrations as the executable source of truth.
- Update `.env.example` and relevant user documentation for new configuration.
- Update `mkdocs.yml` when adding user-facing documentation.
- Add or update a truthful record under `docs/iterations/` for the delivered batch.

Do not replace established project abstractions with parallel implementations. When a service file
exceeds roughly 400 lines, a function exceeds roughly 50 lines, or one service spans three or more
business apps, evaluate use-case-oriented decomposition and document any deliberate deferral.

## Verify

Run focused checks while iterating, then run every repository completion gate:

```bash
make format
make lint
make test
make docs-build
uv lock --check
uv run python manage.py makemigrations --check --dry-run
make check
```

For Agent documentation or Skill changes, also verify Markdown formatting, exact synchronization
between navigated `agent-docs/` sources and `skill/references/`, link/reference completeness, and a
representative Cookiecutter generation scenario.

Report commands exactly as run, their outcomes, and any environmental blocker. Never describe a
failed or skipped check as passed. Do not overwrite unrelated working-tree changes or commit
generated `site/`, secrets, databases, media, caches, or runtime logs.

## Resolve template placeholders

The references originate from a Cookiecutter template. Resolve `__PROJECT_PACKAGE__`,
`__INVALID_EMAIL_DOMAIN__`, and similar placeholders from the generated repository's actual package,
settings, and configuration layout; do not copy placeholder names into production code.

## Use the brand asset

Use [assets/logo.png](assets/logo.png) when a DjangoHarness-branded output explicitly requires the
supplied project logo. Do not modify or regenerate it unless requested.
