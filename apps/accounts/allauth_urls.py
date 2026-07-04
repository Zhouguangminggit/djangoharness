from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="account_login"),
    path("logout/", views.logout_view, name="account_logout"),
    path("signup/", views.register, name="account_signup"),
]
