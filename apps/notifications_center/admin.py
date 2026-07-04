from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from notifications.models import Notification

from .forms import NotificationPublicationAdminForm
from .models import NotificationPublication
from .services import send_notification

User = get_user_model()

if admin.site.is_registered(Notification):
    admin.site.unregister(Notification)


@admin.register(NotificationPublication)
class NotificationPublicationAdmin(admin.ModelAdmin):
    form = NotificationPublicationAdminForm
    list_display = (
        "title",
        "audience",
        "level",
        "created_by",
        "sent_count",
        "published_at",
    )
    list_filter = ("audience", "level", "published_at")
    search_fields = ("title", "body", "created_by__username")
    filter_horizontal = ("recipients",)
    ordering = ("-created_at",)
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.published_at:
            return (
                "title",
                "body",
                "level",
                "target_path",
                "audience",
                "recipients",
                "created_by",
                "published_at",
                "sent_count",
                "created_at",
            )
        return ("created_by", "published_at", "sent_count", "created_at")

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request: HttpRequest, obj, form, change) -> None:
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @transaction.atomic
    def save_related(self, request: HttpRequest, form, formsets, change) -> None:
        super().save_related(request, form, formsets, change)
        publication = NotificationPublication.objects.select_for_update().get(
            pk=form.instance.pk
        )
        if publication.published_at:
            return

        if publication.audience == NotificationPublication.Audience.ALL_ACTIVE:
            recipients = User.objects.filter(is_active=True)
        else:
            recipients = publication.recipients.filter(is_active=True)

        created = send_notification(
            actor=publication.created_by,
            recipients=recipients,
            title=publication.title,
            body=publication.body,
            level=publication.level,
            target_path=publication.target_path,
        )
        publication.published_at = timezone.now()
        publication.sent_count = len(created)
        publication.save(update_fields=("published_at", "sent_count"))
        form.instance.published_at = publication.published_at
        form.instance.sent_count = publication.sent_count
        self.message_user(
            request,
            f"通知已发布，共发送 {publication.sent_count} 条。",
            messages.SUCCESS,
        )
