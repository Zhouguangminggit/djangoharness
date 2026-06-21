from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
LOGGING["root"]["level"] = "DEBUG"  # type: ignore[index]
USE_THIRD_PARTY_SERVICES = False
CACHES["verification"] = {  # type: ignore[index]
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
}
AUTH_FIXED_SMS_CODE = os.environ.get("AUTH_FIXED_SMS_CODE", "246810")
AUTH_FIXED_EMAIL_CODE = os.environ.get("AUTH_FIXED_EMAIL_CODE", "135790")
