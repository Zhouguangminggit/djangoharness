from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_internal_path(value: str) -> None:
    if value and (not value.startswith("/") or value.startswith("//")):
        raise ValidationError("跳转路径必须是以 / 开头的站内路径。")


class NotificationPublication(models.Model):
    class Audience(models.TextChoices):
        ALL_ACTIVE = "all_active", "全部启用用户"
        SELECTED = "selected", "指定用户"

    class Level(models.TextChoices):
        SUCCESS = "success", "成功"
        INFO = "info", "普通"
        WARNING = "warning", "警告"
        ERROR = "error", "错误"

    title = models.CharField("标题", max_length=255)
    body = models.TextField("正文")
    level = models.CharField(
        "级别", max_length=20, choices=Level.choices, default=Level.INFO
    )
    target_path = models.CharField(
        "站内跳转路径",
        max_length=500,
        blank=True,
        validators=[validate_internal_path],
        help_text="可选，只允许以 / 开头的站内路径。",
    )
    audience = models.CharField(
        "收件范围",
        max_length=20,
        choices=Audience.choices,
        default=Audience.SELECTED,
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="指定用户",
        blank=True,
        related_name="notification_publications",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="发布人",
        on_delete=models.PROTECT,
        related_name="created_notification_publications",
    )
    published_at = models.DateTimeField("发布时间", null=True, blank=True)
    sent_count = models.PositiveIntegerField("发送数量", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "通知发布记录"
        verbose_name_plural = "通知发布记录"

    def __str__(self) -> str:
        return self.title
