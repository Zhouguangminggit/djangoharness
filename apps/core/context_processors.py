from django.conf import settings


def site_context(request):
    context = {
        "site_name": "DjangoHarness",
        "auth_style": settings.AUTH_STYLE,
        "auth_media": settings.AUTH_MEDIA,
    }
    if request.user.is_authenticated:
        context["notification_unread_count"] = (
            request.user.notifications.unread().count()
        )
    return context
