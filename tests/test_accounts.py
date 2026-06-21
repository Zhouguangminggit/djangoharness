from io import BytesIO
from typing import Any, cast
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import Client, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.services import (
    VerificationPurpose,
    get_pending_code,
    request_verification_code,
    verify_code,
)
from apps.accounts.tasks import send_verification_code

User = get_user_model()
PASSWORD = "Harness-test-password-2026"


def uploaded_avatar(name: str, color: str = "#66793a") -> SimpleUploadedFile:
    stream = BytesIO()
    Image.new("RGB", (24, 24), color).save(stream, format="PNG")
    return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="member",
        email="member@example.com",
        phone="13800138000",
        password=PASSWORD,
    )


def test_home_page(client: Client) -> None:
    response = client.get(reverse("home"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "把业务想法，落到可靠的工程底座上" in content
    assert "Django Template Framework" not in content


def test_project_templates_are_namespaced() -> None:
    application = cast(Any, get_template("layouts/application.html"))
    home = cast(Any, get_template("core/home.html"))
    admin_base = cast(Any, get_template("admin/base.html"))
    assert application.origin.name.endswith("templates/layouts/application.html")
    assert home.origin.name.endswith("apps/core/templates/core/home.html")
    assert "simpleui/templates/admin/base.html" in admin_base.origin.name
    with pytest.raises(TemplateDoesNotExist):
        get_template("base.html")


@pytest.mark.django_db
@pytest.mark.parametrize("identifier", ["member", "member@example.com", "13800138000"])
def test_authenticate_by_supported_identifier(user, identifier: str) -> None:
    assert authenticate(username=identifier, password=PASSWORD) == user


@pytest.mark.django_db
def test_inactive_user_cannot_authenticate(user) -> None:
    user.is_active = False
    user.save(update_fields=["is_active"])
    assert authenticate(username=user.email, password=PASSWORD) is None


@pytest.mark.django_db
def test_display_name_prefers_nickname_and_masks_mobile_identifier() -> None:
    mobile_user = User.objects.create_user(
        username="mobile_123456789abc",
        email="mobile@example.com",
        phone="13900139000",
        password=PASSWORD,
    )
    assert mobile_user.display_name == "139****9000"
    mobile_user.nickname = "小明"
    assert mobile_user.display_name == "小明"


@patch("apps.accounts.views.send_welcome_email.delay")
@override_settings(USE_THIRD_PARTY_SERVICES=True)
@pytest.mark.django_db
def test_account_register_success(mock_delay, client: Client) -> None:
    response = client.post(
        reverse("accounts:register"),
        {
            "mode": "account",
            "username": "new-user",
            "email": "new-user@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(username="new-user").exists()
    mock_delay.assert_called_once_with("new-user")


@patch("apps.accounts.views.send_welcome_email.delay")
@pytest.mark.django_db
def test_phone_register_with_fixed_code(mock_delay, client: Client) -> None:
    response = client.post(
        reverse("accounts:register"),
        {
            "mode": "phone",
            "phone": "13900139000",
            "code": "246810",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    assert response.status_code == 302
    created_user = User.objects.get(phone="13900139000")
    assert created_user.display_name == "139****9000"
    assert created_user.username.startswith("mobile_")
    mock_delay.assert_not_called()


def test_profile_requires_login(client: Client) -> None:
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_profile_updates_display_and_login_information(user, client: Client) -> None:
    client.force_login(user)
    response = client.post(
        reverse("accounts:profile"),
        {
            "action": "profile",
            "nickname": "工程师小周",
            "username": "zhou-engineer",
            "email": "zhou@example.com",
            "phone": "15000150000",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "个人信息已更新" in response.content.decode()
    assert "工程师小周" in response.content.decode()
    user.refresh_from_db()
    assert user.nickname == "工程师小周"
    assert user.username == "zhou-engineer"
    assert user.email == "zhou@example.com"
    assert user.phone == "13800138000"
    assert authenticate(username="zhou-engineer", password=PASSWORD) == user


@pytest.mark.django_db
def test_profile_rejects_case_insensitive_duplicate_identity(
    user, client: Client
) -> None:
    User.objects.create_user(
        username="existing",
        email="existing@example.com",
        password=PASSWORD,
    )
    client.force_login(user)
    response = client.post(
        reverse("accounts:profile"),
        {
            "action": "profile",
            "nickname": "Member",
            "username": "EXISTING",
            "email": "EXISTING@example.com",
        },
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "该用户名已被使用" in content
    assert "该邮箱已被使用" in content


@pytest.mark.django_db
def test_profile_changes_password_after_old_password_verification(
    user, client: Client
) -> None:
    client.force_login(user)
    rejected = client.post(
        reverse("accounts:profile"),
        {
            "action": "password",
            "old_password": "wrong-password",
            "new_password1": "Changed-password-2026",
            "new_password2": "Changed-password-2026",
        },
    )
    assert "旧密码不正确" in rejected.content.decode()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)

    changed = client.post(
        reverse("accounts:profile"),
        {
            "action": "password",
            "old_password": PASSWORD,
            "new_password1": "Changed-password-2026",
            "new_password2": "Changed-password-2026",
        },
        follow=True,
    )
    assert changed.status_code == 200
    assert "登录密码已修改" in changed.content.decode()
    user.refresh_from_db()
    assert user.check_password("Changed-password-2026")
    assert client.get(reverse("accounts:profile")).status_code == 200


@pytest.mark.django_db
def test_profile_uploads_and_replaces_avatar_in_media(
    user, client: Client, tmp_path
) -> None:
    client.force_login(user)
    with override_settings(MEDIA_ROOT=tmp_path):
        first = client.post(
            reverse("accounts:profile"),
            {
                "action": "profile",
                "nickname": "头像用户",
                "username": user.username,
                "email": user.email,
                "avatar": uploaded_avatar("first.png"),
            },
        )
        assert first.status_code == 302
        user.refresh_from_db()
        first_name = user.avatar.name
        first_path = tmp_path / first_name
        assert first_name.startswith(f"avatars/{user.pk}/")
        assert first_path.exists()

        replaced = client.post(
            reverse("accounts:profile"),
            {
                "action": "profile",
                "nickname": "头像用户",
                "username": user.username,
                "email": user.email,
                "avatar": uploaded_avatar("second.png", "#80541f"),
            },
        )
        assert replaced.status_code == 302
        user.refresh_from_db()
        assert user.avatar.name != first_name
        current_path = tmp_path / user.avatar.name
        assert current_path.exists()
        assert not first_path.exists()
        user.delete()
        assert not current_path.exists()


@pytest.mark.django_db
def test_profile_rejects_non_image_avatar(user, client: Client, tmp_path) -> None:
    client.force_login(user)
    fake_image = SimpleUploadedFile(
        "avatar.png", b"not-an-image", content_type="image/png"
    )
    with override_settings(MEDIA_ROOT=tmp_path):
        response = client.post(
            reverse("accounts:profile"),
            {
                "action": "profile",
                "nickname": "Member",
                "username": user.username,
                "email": user.email,
                "avatar": fake_image,
            },
        )
    assert response.status_code == 200
    assert "avatar" in response.context["profile_form"].errors


@pytest.mark.django_db
def test_profile_contains_inline_password_form_without_reset_link(
    user, client: Client
) -> None:
    client.force_login(user)
    content = client.get(reverse("accounts:profile")).content.decode()
    assert "修改登录密码" in content
    assert 'name="old_password"' in content
    assert reverse("accounts:password_reset") not in content


@pytest.mark.django_db
def test_login_remember_me_and_logout_require_post(user, client: Client) -> None:
    response = client.post(
        reverse("accounts:login"),
        {"identifier": user.email, "password": PASSWORD, "remember_me": "on"},
    )
    assert response.status_code == 302
    assert client.session.get_expire_at_browser_close() is False
    assert client.get(reverse("accounts:logout")).status_code == 405
    logout_response = client.post(reverse("accounts:logout"), follow=True)
    assert logout_response.status_code == 200
    assert 'data-auto-dismiss="3000"' in logout_response.content.decode()
    assert "你已安全退出" in logout_response.content.decode()
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_login_rejects_external_next(user, client: Client) -> None:
    response = client.post(
        f"{reverse('accounts:login')}?next=https://evil.example/",
        {"identifier": user.username, "password": PASSWORD},
    )
    assert response["Location"] == reverse("home")


def test_fixed_verification_codes_do_not_require_redis() -> None:
    assert verify_code(VerificationPurpose.PHONE_REGISTER, "13800138000", "246810")
    assert verify_code(
        VerificationPurpose.PASSWORD_RESET, "member@example.com", "135790"
    )


@override_settings(USE_THIRD_PARTY_SERVICES=False)
@patch("apps.accounts.services.caches")
def test_fixed_code_flow_never_accesses_cache(mock_caches) -> None:
    result = request_verification_code(
        VerificationPurpose.PHONE_REGISTER, "13800138000"
    )
    assert result.accepted is True
    assert verify_code(VerificationPurpose.PHONE_REGISTER, "13800138000", "246810")
    assert get_pending_code(VerificationPurpose.PHONE_REGISTER, "13800138000") is None
    mock_caches.__getitem__.assert_not_called()


def test_development_verification_cache_is_local_memory() -> None:
    assert settings.USE_THIRD_PARTY_SERVICES is False
    assert (
        settings.CACHES["verification"]["BACKEND"]
        == "django.core.cache.backends.locmem.LocMemCache"
    )


@pytest.mark.django_db
def test_code_endpoints_validate_input_and_do_not_enumerate(
    user, client: Client
) -> None:
    assert (
        client.post(reverse("accounts:send_phone_code"), {"phone": "bad"}).status_code
        == 400
    )
    response = client.post(
        reverse("accounts:send_email_code"), {"email": "missing@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "验证码请求已受理"


@pytest.mark.django_db
def test_password_reset_with_email_code(user, client: Client) -> None:
    verify = client.post(
        reverse("accounts:password_reset"),
        {"email": user.email, "code": "135790"},
    )
    assert verify["Location"] == reverse("accounts:password_reset_confirm")

    changed = client.post(
        reverse("accounts:password_reset_confirm"),
        {
            "new_password1": "Changed-password-2026",
            "new_password2": "Changed-password-2026",
        },
    )
    assert changed["Location"] == reverse("accounts:password_reset_complete")
    user.refresh_from_db()
    assert user.check_password("Changed-password-2026")
    assert client.get(reverse("accounts:password_reset_confirm")).status_code == 302


@override_settings(AUTH_STYLE="video")
def test_auth_page_can_render_video(client: Client) -> None:
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200
    assert b"<video" in response.content


@patch("apps.accounts.tasks.provider_for")
@patch("apps.accounts.tasks.get_pending_code", return_value="123456")
@override_settings(USE_THIRD_PARTY_SERVICES=True)
def test_verification_task_dispatches_to_provider(mock_code, mock_provider) -> None:
    send_verification_code.run("phone_register", "13800138000")
    mock_provider.assert_called_once_with("phone_register")
    mock_provider.return_value.send.assert_called_once_with("13800138000", "123456")


@patch("apps.accounts.tasks.provider_for")
@patch("apps.accounts.tasks.get_pending_code", return_value=None)
@override_settings(USE_THIRD_PARTY_SERVICES=True)
def test_verification_task_skips_expired_code(mock_code, mock_provider) -> None:
    send_verification_code.run("password_reset", "member@example.com")
    mock_provider.assert_not_called()


@patch("apps.accounts.tasks.provider_for")
@patch("apps.accounts.tasks.get_pending_code")
@override_settings(USE_THIRD_PARTY_SERVICES=False)
def test_verification_task_skips_all_external_work_locally(
    mock_code, mock_provider
) -> None:
    send_verification_code.run("phone_register", "13800138000")
    mock_code.assert_not_called()
    mock_provider.assert_not_called()
