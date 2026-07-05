from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.db import models


class AIModelConfig(models.Model):
    """可复用的第三方 AI 模型配置。"""

    class Provider(models.TextChoices):
        VOLCANO_ARK = "volcano_ark", "火山方舟"

    name = models.CharField("配置名称", max_length=100)
    provider = models.CharField(
        "服务商", max_length=50, choices=Provider.choices, default=Provider.VOLCANO_ARK
    )
    model_id = models.CharField("模型 ID", max_length=200)
    base_url = models.URLField("API 地址", blank=True)
    api_key = models.CharField("API Key", max_length=500)
    timeout = models.PositiveIntegerField("单次调用超时（秒）", default=60)
    is_active = models.BooleanField("启用", default=True)
    is_default = models.BooleanField("默认配置", default=False)
    extra_config = models.JSONField("扩展参数", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "AI 模型配置"
        verbose_name_plural = "AI 模型配置"
        unique_together = (("provider", "name"),)
        ordering = ("-is_default", "-is_active", "-created_at")

    def __str__(self) -> str:
        default_mark = " [默认]" if self.is_default else ""
        return f"{self.name} ({self.provider}){default_mark}"

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.is_default:
            duplicates = AIModelConfig.objects.filter(
                provider=self.provider, is_default=True
            )
            if self.pk:
                duplicates = duplicates.exclude(pk=self.pk)
            if duplicates.exists():
                raise ValidationError(f"服务商 {self.provider} 只能有一个默认配置。")


class AIGenerationTask(models.Model):
    """AI 生成任务记录，包含状态、结果与错误信息。"""

    class TaskType(models.TextChoices):
        VIDEO = "video", "视频"
        VOICE = "voice", "语音"
        IMAGE_3D = "3d_image", "3D 图像"

    class Status(models.TextChoices):
        PENDING = "pending", "待生成"
        PROCESSING = "processing", "生成中"
        SUCCEEDED = "succeeded", "成功"
        FAILED = "failed", "失败"
        CANCELLED = "cancelled", "已取消"

    config = models.ForeignKey(
        AIModelConfig,
        verbose_name="模型配置",
        on_delete=models.PROTECT,
        related_name="generation_tasks",
    )
    task_type = models.CharField(
        "任务类型",
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.VIDEO,
    )
    status = models.CharField(
        "状态",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    prompt = models.TextField("提示词")
    image = models.ImageField("参考图片", upload_to="ai_images/%Y/%m/", blank=True)
    extra_params = models.JSONField("额外参数", default=dict, blank=True)
    external_task_id = models.CharField("外部任务 ID", max_length=255, blank=True)
    result_url = models.URLField("结果 URL", blank=True)
    result_file = models.FileField(
        "结果文件", upload_to="ai_results/%Y/%m/", blank=True
    )
    error_message = models.TextField("错误信息", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_generation_tasks",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)

    class Meta:
        verbose_name = "AI 生成任务"
        verbose_name_plural = "AI 生成任务"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.get_task_type_display()} - {self.status}"


def ai_result_upload_to(instance: AIGenerationTask, filename: str) -> str:
    extension = Path(filename).suffix.lower() or ".bin"
    return f"ai_results/{instance.pk}/{uuid.uuid4().hex}{extension}"
