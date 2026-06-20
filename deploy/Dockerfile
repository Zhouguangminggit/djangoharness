FROM ghcr.io/astral-sh/uv:0.7.6 AS uv

FROM python:3.12-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev \
    && DJANGO_SETTINGS_MODULE=base_framework.settings.prod \
       DJANGO_SECRET_KEY=build-only-secret \
       DJANGO_ALLOWED_HOSTS=localhost \
       .venv/bin/python manage.py collectstatic --noinput

FROM python:3.12-slim-bookworm AS runtime

ENV DJANGO_SETTINGS_MODULE=base_framework.settings.prod \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl libmariadb3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system django \
    && useradd --system --gid django --home-dir /app django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app
RUN mkdir -p /app/media /app/staticfiles \
    && chown django:django /app /app/media /app/staticfiles

USER django
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:8000/health/ >/dev/null || exit 1

CMD ["gunicorn", "base_framework.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
