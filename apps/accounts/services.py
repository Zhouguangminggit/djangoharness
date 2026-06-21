import hashlib
import secrets
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.core.cache import caches
from django.utils.crypto import constant_time_compare


class VerificationPurpose(str, Enum):
    PHONE_REGISTER = "phone_register"
    PASSWORD_RESET = "password_reset"


class VerificationError(ValueError):
    pass


class VerificationRateLimited(VerificationError):
    pass


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    message: str


def _normalize_target(purpose: VerificationPurpose, target: str) -> str:
    value = target.strip()
    return value.lower() if purpose == VerificationPurpose.PASSWORD_RESET else value


def _key(purpose: VerificationPurpose, target: str) -> str:
    digest = hashlib.sha256(_normalize_target(purpose, target).encode()).hexdigest()
    return f"auth-code:{purpose.value}:{digest}"


def _fixed_code(purpose: VerificationPurpose) -> str:
    if purpose == VerificationPurpose.PHONE_REGISTER:
        return settings.AUTH_FIXED_SMS_CODE
    return settings.AUTH_FIXED_EMAIL_CODE


def request_verification_code(
    purpose: VerificationPurpose, target: str
) -> VerificationResult:
    if not settings.USE_THIRD_PARTY_SERVICES:
        return VerificationResult(True, "验证码已生成，请使用当前环境配置的固定验证码")

    cache = caches["verification"]
    key = _key(purpose, target)
    if cache.get(f"{key}:cooldown"):
        raise VerificationRateLimited("发送过于频繁，请稍后重试")

    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(key, {"code": code, "attempts": 0}, settings.AUTH_CODE_TTL)
    cache.set(f"{key}:cooldown", True, settings.AUTH_CODE_COOLDOWN)

    from .tasks import send_verification_code

    send_verification_code.delay(purpose.value, _normalize_target(purpose, target))
    return VerificationResult(True, "验证码已发送")


def get_pending_code(purpose: VerificationPurpose, target: str) -> str | None:
    if not settings.USE_THIRD_PARTY_SERVICES:
        return None
    payload = caches["verification"].get(_key(purpose, target))
    if not isinstance(payload, dict):
        return None
    code = payload.get("code")
    return code if isinstance(code, str) else None


def verify_code(purpose: VerificationPurpose, target: str, code: str) -> bool:
    if not settings.USE_THIRD_PARTY_SERVICES:
        return constant_time_compare(code.strip(), _fixed_code(purpose))

    cache = caches["verification"]
    key = _key(purpose, target)
    payload = cache.get(key)
    if not isinstance(payload, dict):
        return False
    attempts = int(payload.get("attempts", 0)) + 1
    expected = str(payload.get("code", ""))
    if constant_time_compare(code.strip(), expected):
        cache.delete(key)
        return True
    if attempts >= settings.AUTH_CODE_MAX_ATTEMPTS:
        cache.delete(key)
    else:
        payload["attempts"] = attempts
        cache.set(key, payload, settings.AUTH_CODE_TTL)
    return False
