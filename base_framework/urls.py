from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.core.views import health

urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
