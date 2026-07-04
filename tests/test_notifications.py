import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.test import Client
from django.urls import reverse
from notifications.models import Notification

from apps.notifications_center.models import NotificationPublication
from apps.notifications_center.services import send_notification

User = get_user_model()
PASSWORD = "Harness-test-password-2026"


@pytest.fixture
def users(db):
    actor = User.objects.create_user(
        username="actor", email="actor@example.com", password=PASSWORD
    )
    recipient = User.objects.create_user(
        username="recipient", email="recipient@example.com", password=PASSWORD
    )
    other = User.objects.create_user(
        username="other", email="other@example.com", password=PASSWORD
    )
    return actor, recipient, other


@pytest.mark.django_db
def test_service_sends_to_unique_recipients_with_data_and_objects(users) -> None:
    actor, recipient, other = users

    created = send_notification(
        actor=actor,
        recipients=[recipient, recipient, other],
        title="状态已更新",
        body="审批流程已完成。",
        level="success",
        target_path="/orders/1/",
        action_object=recipient,
        target=other,
    )

    assert len(created) == 2
    notification = Notification.objects.get(recipient=recipient)
    assert notification.verb == "状态已更新"
    assert notification.description == "审批流程已完成。"
    assert notification.level == "success"
    assert notification.data == {"target_path": "/orders/1/"}
    assert notification.action_object == recipient
    assert notification.target == other


@pytest.mark.django_db
def test_service_accepts_one_recipient_and_empty_recipients(users) -> None:
    actor, recipient, _ = users

    assert (
        len(send_notification(actor=actor, recipients=recipient, title="单用户消息"))
        == 1
    )
    assert send_notification(actor=actor, recipients=[], title="空消息") == []


@pytest.mark.django_db
@pytest.mark.parametrize("target_path", ["https://example.com", "//example.com"])
def test_service_rejects_non_internal_target_path(users, target_path: str) -> None:
    actor, recipient, _ = users

    with pytest.raises(ValidationError):
        send_notification(
            actor=actor,
            recipients=recipient,
            title="非法链接",
            target_path=target_path,
        )


@pytest.mark.django_db
def test_service_rejects_invalid_level(users) -> None:
    actor, recipient, _ = users

    with pytest.raises(ValidationError):
        send_notification(
            actor=actor,
            recipients=recipient,
            title="非法级别",
            level="critical",
        )


@pytest.mark.django_db
def test_admin_publishes_to_selected_users_once(client: Client, users) -> None:
    admin_user, recipient, other = users
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save(update_fields=("is_staff", "is_superuser"))
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:notifications_center_notificationpublication_add"),
        {
            "title": "维护通知",
            "body": "今晚进行系统维护。",
            "level": "warning",
            "target_path": "/",
            "audience": "selected",
            "recipients": [recipient.pk],
            "_save": "保存",
        },
    )

    assert response.status_code == 302
    publication = NotificationPublication.objects.get()
    assert publication.created_by == admin_user
    assert publication.published_at is not None
    assert publication.sent_count == 1
    assert Notification.objects.filter(recipient=recipient).count() == 1
    assert not Notification.objects.filter(recipient=other).exists()

    response = client.post(
        reverse(
            "admin:notifications_center_notificationpublication_change",
            args=(publication.pk,),
        ),
        {"_save": "保存"},
    )
    assert response.status_code == 302
    assert Notification.objects.count() == 1


@pytest.mark.django_db
def test_admin_broadcasts_only_to_active_users(client: Client, users) -> None:
    admin_user, active_user, inactive_user = users
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save(update_fields=("is_staff", "is_superuser"))
    inactive_user.is_active = False
    inactive_user.save(update_fields=("is_active",))
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:notifications_center_notificationpublication_add"),
        {
            "title": "广播",
            "body": "面向启用用户。",
            "level": "info",
            "target_path": "",
            "audience": "all_active",
            "_save": "保存",
        },
    )

    assert response.status_code == 302
    assert set(Notification.objects.values_list("recipient_id", flat=True)) == {
        admin_user.pk,
        active_user.pk,
    }
    assert NotificationPublication.objects.get().sent_count == 2


@pytest.mark.django_db
def test_admin_requires_selected_recipient(client: Client, users) -> None:
    admin_user, _, _ = users
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save(update_fields=("is_staff", "is_superuser"))
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:notifications_center_notificationpublication_add"),
        {
            "title": "无收件人",
            "body": "不会发布。",
            "level": "info",
            "audience": "selected",
            "_save": "保存",
        },
    )

    assert response.status_code == 200
    assert "至少需要选择一名用户" in response.content.decode()
    assert not NotificationPublication.objects.exists()


@pytest.mark.django_db
def test_notification_list_requires_login_and_shows_only_owners_messages(
    client: Client, users
) -> None:
    actor, recipient, other = users
    send_notification(actor=actor, recipients=recipient, title="我的消息")
    send_notification(actor=actor, recipients=other, title="他人消息")
    url = reverse("notifications_center:list")

    anonymous_response = client.get(url)
    assert anonymous_response.status_code == 302
    assert reverse("accounts:login") in anonymous_response.headers["Location"]

    client.force_login(recipient)
    response = client.get(url)
    assert response.status_code == 200
    assert "我的消息" in response.content.decode()
    assert "他人消息" not in response.content.decode()


@pytest.mark.django_db
def test_notification_filters_paginates_and_header_shows_unread_count(
    client: Client, users
) -> None:
    actor, recipient, _ = users
    send_notification(
        actor=actor,
        recipients=[recipient] * 21,
        title="去重后消息",
    )
    for index in range(20):
        send_notification(actor=actor, recipients=recipient, title=f"消息 {index}")
    Notification.objects.filter(recipient=recipient).first().mark_as_read()
    client.force_login(recipient)

    all_response = client.get(reverse("notifications_center:list"))
    assert all_response.context["page"].paginator.count == 21
    assert "20 条未读消息" in all_response.content.decode()

    unread_response = client.get(
        reverse("notifications_center:list"), {"status": "unread"}
    )
    read_response = client.get(reverse("notifications_center:list"), {"status": "read"})
    assert unread_response.context["page"].paginator.count == 20
    assert read_response.context["page"].paginator.count == 1


@pytest.mark.django_db
def test_user_can_change_own_read_state_and_mark_all_read(
    client: Client, users
) -> None:
    actor, recipient, _ = users
    notification = send_notification(
        actor=actor, recipients=recipient, title="状态消息"
    )[0]
    client.force_login(recipient)

    response = client.post(
        reverse("notifications_center:mark_read", args=(notification.pk,))
    )
    assert response.status_code == 302
    notification.refresh_from_db()
    assert notification.unread is False

    client.post(reverse("notifications_center:mark_unread", args=(notification.pk,)))
    notification.refresh_from_db()
    assert notification.unread is True

    client.post(reverse("notifications_center:mark_all_read"))
    notification.refresh_from_db()
    assert notification.unread is False


@pytest.mark.django_db
def test_user_cannot_change_another_users_notification(client: Client, users) -> None:
    actor, recipient, other = users
    notification = send_notification(actor=actor, recipients=other, title="他人消息")[0]
    client.force_login(recipient)

    response = client.post(
        reverse("notifications_center:mark_read", args=(notification.pk,))
    )

    assert response.status_code == 404
    notification.refresh_from_db()
    assert notification.unread is True


@pytest.mark.django_db
def test_read_state_rejects_external_next_redirect(client: Client, users) -> None:
    actor, recipient, _ = users
    notification = send_notification(
        actor=actor, recipients=recipient, title="安全跳转"
    )[0]
    client.force_login(recipient)

    response = client.post(
        reverse("notifications_center:mark_read", args=(notification.pk,)),
        {"next": "https://example.com/phishing"},
    )

    assert response.headers["Location"] == reverse("notifications_center:list")


@pytest.mark.django_db
def test_read_state_endpoints_require_post_and_csrf(users) -> None:
    actor, recipient, _ = users
    notification = send_notification(
        actor=actor, recipients=recipient, title="CSRF 消息"
    )[0]
    client = Client(enforce_csrf_checks=True)
    client.force_login(recipient)
    url = reverse("notifications_center:mark_read", args=(notification.pk,))

    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 403


@pytest.mark.django_db
def test_header_hides_notification_entry_for_anonymous_user(client: Client) -> None:
    response = client.get(reverse("home"))

    assert reverse("notifications_center:list") not in response.content.decode()


def test_notification_template_uses_project_namespace() -> None:
    template = get_template("notifications_center/list.html")

    assert "apps/notifications_center/templates" in str(getattr(template, "origin", ""))
