from apps.accounts.tasks import send_welcome_email


def test_send_welcome_email() -> None:
    assert send_welcome_email.run("Ada") == "welcome Ada"
