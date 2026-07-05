from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("codes/phone/", views.send_phone_code, name="send_phone_code"),
    path("codes/email/", views.send_email_code, name="send_email_code"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path(
        "password-reset/confirm/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "password-reset/done/",
        views.password_reset_complete,
        name="password_reset_done",
    ),
    path(
        "reset/done/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),
]
