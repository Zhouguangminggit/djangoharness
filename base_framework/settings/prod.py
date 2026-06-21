from base_framework.logging import configure_logging

from .base import *

DEBUG = False
ALLOWED_HOSTS = get_env_list("DJANGO_ALLOWED_HOSTS", "")
CSRF_TRUSTED_ORIGINS = [
    origin for origin in get_env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "") if origin
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

USE_THIRD_PARTY_SERVICES = get_env_bool(
    "USE_THIRD_PARTY_SERVICES", get_env_bool("USE_THREE_SERIVCE", True)
)
if USE_THIRD_PARTY_SERVICES:
    CACHES["verification"] = {  # type: ignore[index]
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": AUTH_VERIFICATION_REDIS_URL,
    }

LOG_COLORIZE = get_env_bool("LOG_COLORIZE", True)
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
