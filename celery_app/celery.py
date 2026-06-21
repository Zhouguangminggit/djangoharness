import os
from logging import Logger
from typing import Any

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from base_framework.logging import InterceptHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base_framework.settings.dev")

app = Celery("base_framework")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


def _configure_celery_logger(logger: Logger, **_: Any) -> None:
    logger.handlers = [InterceptHandler()]
    logger.propagate = False


after_setup_logger.connect(_configure_celery_logger)
after_setup_task_logger.connect(_configure_celery_logger)
