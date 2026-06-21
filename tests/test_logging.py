import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from loguru import logger

from apps.core.middleware import RequestLoggingMiddleware
from base_framework.logging import InterceptHandler, configure_logging
from celery_app.celery import _configure_celery_logger


def test_development_logging_suppresses_debug() -> None:
    assert logging.getLogger("apps.example").getEffectiveLevel() == logging.INFO
    assert (
        logging.getLogger("django.utils.autoreload").getEffectiveLevel() == logging.INFO
    )


def test_loguru_writes_colored_console_and_plain_rotating_file(
    capfd: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    app_log_file = tmp_path / "logs" / "app.log"
    async_log_file = tmp_path / "logs" / "async.log"
    error_log_file = tmp_path / "logs" / "error.log"
    standard_logger = logging.getLogger("tests.loguru_bridge")
    original_handlers = standard_logger.handlers[:]
    original_propagate = standard_logger.propagate
    standard_logger.handlers = [InterceptHandler()]
    standard_logger.propagate = False
    standard_logger.setLevel(logging.INFO)

    try:
        configure_logging(
            level="INFO",
            colorize=True,
            file_enabled=True,
            app_file_path=app_log_file,
            async_file_path=async_log_file,
            error_file_path=error_log_file,
            rotation="1 MB",
            retention="1 day",
            compression="gz",
            backtrace=False,
            diagnose=False,
        )
        logger.debug("hidden debug message")
        standard_logger.warning("bridge message")
        logger.bind(request_id="request-123").info("bound context")
        logger.bind(source="apps.accounts.tasks").info("async message")
        logger.error("error message")

        captured = capfd.readouterr()
        assert "\x1b[" in captured.err
        assert "hidden debug message" not in captured.err
        assert "bridge message" in captured.err
        assert "test_loguru_writes_colored_console" in captured.err
        assert "request-123" in captured.err

        app_file_content = app_log_file.read_text(encoding="utf-8")
        assert "bridge message" in app_file_content
        assert "request-123" in app_file_content
        assert "async message" not in app_file_content
        assert "hidden debug message" not in app_file_content
        assert "\x1b[" not in app_file_content
        assert "async message" in async_log_file.read_text(encoding="utf-8")
        assert "error message" in error_log_file.read_text(encoding="utf-8")
    finally:
        standard_logger.handlers = original_handlers
        standard_logger.propagate = original_propagate
        logger.remove()


def test_celery_logger_uses_loguru_bridge() -> None:
    celery_logger = logging.Logger("celery.test")
    celery_logger.addHandler(logging.NullHandler())

    _configure_celery_logger(celery_logger)

    assert len(celery_logger.handlers) == 1
    assert isinstance(celery_logger.handlers[0], InterceptHandler)
    assert celery_logger.propagate is False


def test_request_log_contains_safe_user_context(tmp_path: Path) -> None:
    app_log_file = tmp_path / "logs" / "app.log"
    configure_logging(
        level="INFO",
        colorize=False,
        file_enabled=True,
        app_file_path=app_log_file,
        async_file_path=tmp_path / "logs" / "async.log",
        error_file_path=tmp_path / "logs" / "error.log",
        rotation="1 MB",
        retention="1 day",
        compression="gz",
        backtrace=False,
        diagnose=False,
    )
    request = RequestFactory().get(
        "/health/", HTTP_X_REQUEST_ID="request-456", REMOTE_ADDR="127.0.0.1"
    )
    cast(Any, request).user = SimpleNamespace(
        pk=42,
        is_authenticated=True,
        get_username=lambda: "13800138000",
    )
    middleware = RequestLoggingMiddleware(lambda _: HttpResponse("ok", status=200))

    try:
        response = middleware(request)
        file_content = app_log_file.read_text(encoding="utf-8")

        assert response["X-Request-ID"] == "request-456"
        assert "'request_id': 'request-456'" in file_content
        assert "'user_id': '42'" in file_content
        assert "'username': '138****8000'" in file_content
        assert "'client_ip': '127.0.0.1'" in file_content
        assert "'method': 'GET'" in file_content
        assert "'path': '/health/'" in file_content
        assert "13800138000" not in file_content
    finally:
        logger.remove()
