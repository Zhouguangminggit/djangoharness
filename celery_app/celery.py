import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base_framework.settings.dev")

app = Celery("base_framework")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
