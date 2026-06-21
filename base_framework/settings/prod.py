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
