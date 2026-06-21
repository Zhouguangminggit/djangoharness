from django.conf import settings


def site_context(request):
    return {
        "site_name": "DjangoHarness",
        "auth_style": settings.AUTH_STYLE,
        "auth_media": settings.AUTH_MEDIA,
    }
