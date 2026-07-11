import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

User = get_user_model()
PASSWORD = "Harness-test-password-2026"


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password=PASSWORD,
    )


def test_admin_dashboard_requires_login(client: Client) -> None:
    response = client.get(reverse("admin:index"))

    assert response.status_code == 302
    assert response.headers["Location"].startswith(reverse("admin:login"))


@pytest.mark.django_db
def test_admin_dashboard_shows_user_metrics(admin_user, client: Client) -> None:
    User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        password=PASSWORD,
        is_active=False,
    )
    client.force_login(admin_user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "用户数据概览" in content
    assert "最近六个月新增用户" in content
    assert "账号状态" in content
    assert reverse("admin:accounts_user_bulk_add") in content
    assert "__PRODUCT_NAME__" in content
    assert "__PRODUCT_SUBTITLE__" in content
    assert "admin/css/theme.css" in content


@pytest.mark.django_db
def test_admin_user_crud_pages_are_available(admin_user, client: Client) -> None:
    client.force_login(admin_user)
    urls = (
        reverse("admin:accounts_user_changelist"),
        reverse("admin:accounts_user_add"),
        reverse("admin:accounts_user_change", args=(admin_user.pk,)),
        reverse("admin:accounts_user_delete", args=(admin_user.pk,)),
    )

    for url in urls:
        assert client.get(url).status_code == 200

    add_content = client.get(reverse("admin:accounts_user_add")).content.decode()
    assert "基本信息" in add_content
    assert "个人信息" in add_content
    assert "权限" in add_content
    assert 'name="is_active"' in add_content

    change_content = client.get(
        reverse("admin:accounts_user_change", args=(admin_user.pk,))
    ).content.decode()
    assert "重要日期" in change_content
    assert "控制后台访问、角色分组和细粒度权限" in change_content


@pytest.mark.django_db
def test_group_admin_uses_unfold(admin_user, client: Client) -> None:
    client.force_login(admin_user)

    response = client.get(reverse("admin:auth_group_changelist"))

    assert response.status_code == 200
    assert "unfold/css/styles.css" in response.content.decode()


@pytest.mark.django_db
def test_bulk_user_import_creates_all_valid_rows(admin_user, client: Client) -> None:
    client.force_login(admin_user)
    content = (
        "username,email,password,nickname,phone,is_staff,is_active\n"
        "alice,alice@example.com,Harness-alice-2026,艾丽丝,13800138001,false,true\n"
        "bob,bob@example.com,Harness-bob-2026,鲍勃,,true,true\n"
    )

    response = client.post(
        reverse("admin:accounts_user_bulk_add"),
        {"csv_file": SimpleUploadedFile("users.csv", content.encode())},
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse("admin:accounts_user_changelist"), 302)]
    assert User.objects.get(username="alice").check_password("Harness-alice-2026")
    assert User.objects.get(username="bob").is_staff is True


@pytest.mark.django_db
def test_bulk_user_import_rejects_whole_file_on_duplicate(
    admin_user, client: Client
) -> None:
    client.force_login(admin_user)
    content = (
        "username,email,password\n"
        "new-user,new@example.com,Harness-new-2026\n"
        "admin,another@example.com,Harness-another-2026\n"
    )

    response = client.post(
        reverse("admin:accounts_user_bulk_add"),
        {"csv_file": SimpleUploadedFile("users.csv", content.encode())},
    )

    assert response.status_code == 200
    assert "用户名已存在" in response.content.decode()
    assert not User.objects.filter(username="new-user").exists()


@pytest.mark.django_db
def test_bulk_user_import_requires_add_permission(client: Client) -> None:
    staff = User.objects.create_user(
        username="readonly",
        email="readonly@example.com",
        password=PASSWORD,
        is_staff=True,
    )
    client.force_login(staff)

    response = client.get(reverse("admin:accounts_user_bulk_add"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_user_actions_preserve_current_account(
    admin_user, client: Client
) -> None:
    inactive = User.objects.create_user(
        username="inactive-action",
        email="inactive-action@example.com",
        password=PASSWORD,
        is_active=False,
    )
    active = User.objects.create_user(
        username="active-action",
        email="active-action@example.com",
        password=PASSWORD,
        is_active=True,
    )
    client.force_login(admin_user)
    changelist = reverse("admin:accounts_user_changelist")

    response = client.post(
        changelist,
        {
            "action": "activate_users",
            "_selected_action": [inactive.pk],
        },
        follow=True,
    )
    assert response.status_code == 200
    inactive.refresh_from_db()
    assert inactive.is_active is True

    response = client.post(
        changelist,
        {
            "action": "deactivate_users",
            "_selected_action": [admin_user.pk, active.pk],
        },
        follow=True,
    )
    assert response.status_code == 200
    admin_user.refresh_from_db()
    active.refresh_from_db()
    assert admin_user.is_active is True
    assert active.is_active is False
