from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import application_home, health, product_introduction

urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.allauth_urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("notifications/", include("apps.notifications_center.urls")),
    path("blog/", include("apps.blog.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", product_introduction, name="product_introduction"),
    path("", product_introduction, name="home"),
    path("app/", application_home, name="app_home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
