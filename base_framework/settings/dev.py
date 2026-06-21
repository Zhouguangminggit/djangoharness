from base_framework.logging import configure_logging

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_COLORIZE = get_env_bool("LOG_COLORIZE", True)
LOG_FILE_ENABLED = get_env_bool("LOG_FILE_ENABLED", True)
LOGGING["root"]["level"] = LOG_LEVEL  # type: ignore[index]
for logger_name, logger_config in LOGGING["loggers"].items():  # type: ignore[union-attr]
    if logger_name != "django.utils.autoreload":
        logger_config["level"] = LOG_LEVEL
USE_THIRD_PARTY_SERVICES = False
CACHES["verification"] = {  # type: ignore[index]
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
}
AUTH_FIXED_SMS_CODE = os.environ.get("AUTH_FIXED_SMS_CODE", "246810")
AUTH_FIXED_EMAIL_CODE = os.environ.get("AUTH_FIXED_EMAIL_CODE", "135790")

configure_logging(
    level=LOG_LEVEL,
    colorize=LOG_COLORIZE,
    file_enabled=LOG_FILE_ENABLED,
    app_file_path=LOG_FILE_PATH,
    async_file_path=LOG_ASYNC_FILE_PATH,
    error_file_path=LOG_ERROR_FILE_PATH,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    compression=LOG_COMPRESSION,
    backtrace=LOG_BACKTRACE,
    diagnose=LOG_DIAGNOSE,
)
