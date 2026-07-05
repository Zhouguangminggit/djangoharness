"""Django project package.

The Celery application lives in :mod:`celery_app`.  Do not import it here:
``celery_app.celery`` imports ``__PROJECT_PACKAGE__.logging`` while bootstrapping,
so exporting it from this package would create a circular import.
"""
