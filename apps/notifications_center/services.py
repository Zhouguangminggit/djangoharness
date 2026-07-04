from collections.abc import Iterable
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Model
from notifications.models import Notification
from notifications.signals import notify

from .models import validate_internal_path

User = get_user_model()
VALID_LEVELS = {choice[0] for choice in Notification.LEVELS}


def send_notification(
    *,
    actor: Model,
    recipients: Iterable[Any] | Any,
    title: str,
    body: str = "",
    level: str = "info",
    target_path: str = "",
    action_object: Model | None = None,
    target: Model | None = None,
) -> list[Notification]:
    """Create one in-app notification per unique recipient."""
    validate_internal_path(target_path)
    if level not in VALID_LEVELS:
        raise ValidationError("无效的通知级别。")

    if isinstance(recipients, User):
        recipient_items = [recipients]
    else:
        recipient_items = list(recipients)

    unique_recipients = list(
        {
            recipient.pk: recipient for recipient in recipient_items if recipient.pk
        }.values()
    )
    if not unique_recipients:
        return []

    responses = notify.send(
        sender=actor,
        recipient=unique_recipients,
        verb=title,
        description=body,
        level=level,
        action_object=action_object,
        target=target,
        target_path=target_path,
    )
    created: list[Notification] = []
    for _, response in responses:
        if response:
            created.extend(response)
    return created
