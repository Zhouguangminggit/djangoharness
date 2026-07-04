from allauth.account.models import EmailAddress
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import User


@receiver(post_delete, sender=User)
def delete_user_avatar(sender, instance: User, **kwargs) -> None:
    if instance.avatar:
        instance.avatar.delete(save=False)


def sync_primary_email(user: User) -> None:
    if user.email.endswith("@mobile.djangoharness.invalid"):
        EmailAddress.objects.filter(user=user).delete()
        return
    with transaction.atomic():
        EmailAddress.objects.filter(user=user).exclude(email=user.email).delete()
        EmailAddress.objects.filter(user=user, primary=True).update(primary=False)
        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"primary": True, "verified": True},
        )
