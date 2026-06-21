import logging

from celery import shared_task
from django.conf import settings

from .providers import provider_for
from .services import VerificationPurpose, get_pending_code

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(username: str) -> str:
    return f"welcome {username}"


@shared_task(
    autoretry_for=(OSError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
    soft_time_limit=20,
    time_limit=30,
)
def send_verification_code(purpose: str, target: str) -> None:
    if not settings.USE_THIRD_PARTY_SERVICES:
        logger.info("第三方服务已关闭，取消验证码发送 purpose=%s", purpose)
        return
    verification_purpose = VerificationPurpose(purpose)
    code = get_pending_code(verification_purpose, target)
    if code is None:
        logger.info("验证码已过期，取消发送 purpose=%s", purpose)
        return
    provider_for(purpose).send(target, code)
