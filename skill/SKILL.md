---
name: djangoharness
description: Implement, modify, review, and verify DjangoHarness modules using the repository's Django 4.2, Python 3.10+, Celery, Redis, pytest-django, Ruff, mypy, uv, MySQL 8 reference SQL, and AI-oriented engineering conventions. Use for DjangoHarness work involving apps, models, migrations, SQL, views, forms, URLs, templates, static assets, settings, permissions, authentication, asynchronous tasks, dependencies, tests, deployment-adjacent configuration, iteration notes, or acceptance fixes.
---

# DjangoHarness

## Execute the workflow

1. Inspect the repository and preserve unrelated user changes.
2. Read [project-structure.md](references/project-structure.md) before changing code.
3. Load only the task-specific references:
   - Django apps, models, views, forms, URLs, templates, or static assets: read [django-development.md](references/django-development.md).
   - Models, migrations, schema, indexes, or SQL: also read [database.md](references/database.md).
   - Celery tasks, retries, brokers, results, or Redis: read [async-tasks.md](references/async-tasks.md).
   - Dependencies, formatting, typing, tests, or delivery: read [engineering-quality.md](references/engineering-quality.md).
4. Trace existing patterns before implementing. Keep the change scoped to the requested business domain.
5. Implement the smallest complete change, including tests and synchronized artifacts required by the references.
6. Run focused checks during development, then run the completion checks.
7. Update or add the relevant record under `docs/iterations/` with the actual changes, verification results, and remaining issues.

## Apply architectural boundaries

- Put each business domain in `apps/<business_name>/`; put genuinely cross-domain capabilities in `apps/core/`.
- Keep views at the HTTP orchestration boundary, forms at the input-validation boundary, and complex business rules in independently testable service functions.
- Keep project URLs limited to mounting app URLs. Use `app_name`, named routes, `reverse`, and `{% url %}`.
- Keep secrets, domains, databases, and external service addresses in environment variables. Synchronize new variables to `.env.example`.
- Preserve Python 3.10+ and Django 4.2 compatibility unless the request explicitly changes the support policy.
- Do not silently change established URL names, template paths, authentication behavior, or public interfaces.

## Handle cross-cutting changes

For a business model change, always keep these artifacts aligned:

1. Django model definition.
2. Django migration generated with `uv run python manage.py makemigrations`.
3. Matching MySQL 8 reference definition in `db/*.sql`.
4. Model and behavior tests.

Treat migrations as the only executable schema source. Treat `db/*.sql` as review and non-Django deployment references, never as a replacement for migrations.

For asynchronous work, pass small JSON-serializable arguments, preferably entity IDs. Make tasks retryable and as idempotent as practical. Keep complex logic in ordinary testable Python services; test callers by mocking `.delay()` and do not require a real Redis service for the standard test suite.

## Verify completion

Run focused tests first when useful. Before declaring a batch complete, run:

```bash
make format
make lint
make test
```

Also run `uv lock --check` and `make check` before merge. For model work, additionally run:

```bash
uv run python manage.py makemigrations --check --dry-run
```

Report command results exactly. Do not describe a failed or skipped check as passing. If a check cannot run because of the environment, state the concrete blocker and retain the required follow-up in the iteration record.

## Use the brand asset

Use [logo.png](assets/logo.png) when a DjangoHarness-branded output explicitly requires the supplied project logo. Do not modify or regenerate it unless requested.
