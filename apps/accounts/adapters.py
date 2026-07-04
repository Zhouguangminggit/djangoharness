import re
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.http import url_has_allowed_host_and_scheme

from .services import VerificationPurpose, request_verification_code


def user_display(user: AbstractBaseUser) -> str:
    return str(getattr(user, "display_name", user))


class AccountAdapter(DefaultAccountAdapter):
    """Bridge django-allauth account hooks to DjangoHarness identities."""

    def phone_form_field(self, **kwargs: Any) -> forms.CharField:
        kwargs.setdefault("label", "手机号")
        kwargs.setdefault(
            "widget",
            forms.TextInput(
                attrs={"type": "tel", "autocomplete": "tel", "placeholder": "手机号"}
            ),
        )
        return forms.CharField(max_length=20, **kwargs)

    def is_safe_url(self, url: str) -> bool:
        if not self.request:
            return False
        return url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

    def clean_phone(self, phone: str) -> str:
        value = phone.strip()
        if not re.fullmatch(r"1\d{10}", value):
            raise forms.ValidationError("请输入有效的中国大陆手机号")
        return value

    def get_phone(self, user: AbstractBaseUser) -> tuple[str, bool] | None:
        phone = getattr(user, "phone", None)
        if not phone:
            return None
        return phone, bool(getattr(user, "phone_verified", False))

    def set_phone(self, user: AbstractBaseUser, phone: str, verified: bool) -> None:
        user.phone = self.clean_phone(phone)  # type: ignore[attr-defined]
        user.phone_verified = verified  # type: ignore[attr-defined]
        user.save(update_fields=["phone", "phone_verified"])

    def set_phone_verified(self, user: AbstractBaseUser, phone: str) -> None:
        if getattr(user, "phone", None) != phone:
            self.set_phone(user, phone, True)
            return
        user.phone_verified = True  # type: ignore[attr-defined]
        user.save(update_fields=["phone_verified"])

    def get_user_by_phone(self, phone: str) -> AbstractBaseUser | None:
        user_model = get_user_model()
        return user_model.objects.filter(phone=self.clean_phone(phone)).first()

    def generate_phone_verification_code(
        self, *, user: AbstractBaseUser, phone: str
    ) -> str:
        if not settings.USE_THIRD_PARTY_SERVICES:
            return settings.AUTH_FIXED_SMS_CODE
        return super().generate_phone_verification_code(user=user, phone=phone)

    def generate_password_reset_code(self) -> str:
        if not settings.USE_THIRD_PARTY_SERVICES:
            return settings.AUTH_FIXED_EMAIL_CODE
        return super().generate_password_reset_code()

    def send_verification_code_sms(
        self, user: AbstractBaseUser, phone: str, code: str, **kwargs: Any
    ) -> None:
        request_verification_code(VerificationPurpose.PHONE_REGISTER, phone, code=code)

    def send_mail(
        self,
        template_prefix: str,
        email: str,
        context: dict[str, Any],
    ) -> None:
        if template_prefix == "account/email/password_reset_code":
            code = str(context["code"])
            request_verification_code(
                VerificationPurpose.PASSWORD_RESET, email, code=code
            )
            return None
        return super().send_mail(template_prefix, email, context)
