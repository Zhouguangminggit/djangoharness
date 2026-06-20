from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


def test_home_page(client: Client) -> None:
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert "Django Template Framework" in response.content.decode()


def test_register_page(client: Client) -> None:
    response = client.get(reverse("accounts:register"))

    assert response.status_code == 200


@patch("apps.accounts.views.send_welcome_email.delay")
@pytest.mark.django_db
def test_register_success(mock_delay: object, client: Client) -> None:
    response = client.post(
        reverse("accounts:register"),
        {
            "username": "new-user",
            "email": "new-user@example.com",
            "password1": "Harness-test-password-2026",
            "password2": "Harness-test-password-2026",
        },
    )

    assert response.status_code == 302
    assert response["Location"] == reverse("home")
    assert get_user_model().objects.filter(username="new-user").exists()
    mock_delay.assert_called_once_with("new-user")  # type: ignore[attr-defined]
