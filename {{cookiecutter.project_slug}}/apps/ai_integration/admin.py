from __future__ import annotations

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from .forms import AIGenerationTaskAdminForm
from .models import AIGenerationTask, AIModelConfig
from .services import download_result
from .tasks import execute_ai_generation_task


@admin.register(AIModelConfig)
class AIModelConfigAdmin(ModelAdmin):
    formfield_overrides = {
        "api_key": {"widget": forms.PasswordInput(render_value=True)},
    }
    list_display = (
        "name",
        "provider",
        "model_id",
        "timeout",
        "is_active",
        "is_default",
        "updated_at",
    )
    list_filter = ("provider", "is_active", "is_default")
    search_fields = ("name", "model_id")
    ordering = ("-is_default", "-is_active", "-created_at")
    list_per_page = 20
    list_filter_submit = True
    list_fullwidth = True
    actions = ("set_as_default",)

    @action(
        description="设为默认配置",
        icon="star",
        variant=ActionVariant.SUCCESS,
    )
    def set_as_default(self, request: HttpRequest, queryset) -> None:
        updated = 0
        for config in queryset:
            config.is_default = True
            config.save(update_fields=["is_default"])
            updated += 1
        self.message_user(request, f"已将 {updated} 条配置设为默认。", messages.SUCCESS)


@admin.register(AIGenerationTask)
class AIGenerationTaskAdmin(ModelAdmin):
    form = AIGenerationTaskAdminForm
    list_display = (
        "id",
        "task_type",
        "status_colored",
        "prompt_short",
        "config",
        "created_by",
        "created_at",
        "started_at",
        "completed_at",
        "operations",
    )
    list_filter = ("task_type", "status", "config")
    search_fields = ("prompt", "external_task_id", "error_message")
    ordering = ("-created_at",)
    list_per_page = 20
    list_filter_submit = True
    list_fullwidth = True
    readonly_fields = (
        "status",
        "external_task_id",
        "result_url",
        "result_file",
        "error_message",
        "created_by",
        "created_at",
        "started_at",
        "completed_at",
    )
    actions = ("retry_selected_tasks",)

    class Media:
        css = {"all": ("ai_integration/css/admin.css",)}

    fieldsets = (
        (
            "生成配置",
            {
                "fields": ("config", "task_type", "prompt", "image", "extra_params"),
                "description": "选择模型配置并填写提示词与可选参考图片。",
            },
        ),
        (
            "执行结果",
            {
                "fields": (
                    "status",
                    "external_task_id",
                    "result_url",
                    "result_file",
                    "error_message",
                ),
                "description": "任务状态由 Celery 异步任务自动更新。",
            },
        ),
        (
            "时间记录",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "started_at",
                    "completed_at",
                ),
            },
        ),
    )

    STATUS_COLORS = {
        AIGenerationTask.Status.PENDING.value: ("gray", "待生成"),
        AIGenerationTask.Status.PROCESSING.value: ("blue", "生成中"),
        AIGenerationTask.Status.SUCCEEDED.value: ("green", "成功"),
        AIGenerationTask.Status.FAILED.value: ("red", "失败"),
        AIGenerationTask.Status.CANCELLED.value: ("orange", "已取消"),
    }

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/generate/",
                self.admin_site.admin_view(self.generate_task_view),
                name=f"{self.opts.app_label}_{self.opts.model_name}_generate",
            ),
            path(
                "<path:object_id>/download/",
                self.admin_site.admin_view(self.download_result_view),
                name=f"{self.opts.app_label}_{self.opts.model_name}_download",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="提示词")
    def prompt_short(self, obj: AIGenerationTask) -> str:
        if len(obj.prompt) <= 40:
            return obj.prompt
        return obj.prompt[:40] + "..."

    @admin.display(description="状态")
    def status_colored(self, obj: AIGenerationTask) -> str:
        color, label = self.STATUS_COLORS.get(
            obj.status, ("gray", obj.get_status_display())
        )
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color,
            label,
        )

    @admin.display(description="操作")
    def operations(self, obj: AIGenerationTask) -> str:
        generate_url = reverse(
            f"admin:{self.opts.app_label}_{self.opts.model_name}_generate",
            args=(obj.pk,),
        )
        download_url = reverse(
            f"admin:{self.opts.app_label}_{self.opts.model_name}_download",
            args=(obj.pk,),
        )

        is_processing = obj.status == AIGenerationTask.Status.PROCESSING
        generate_class = (
            "ai-action-btn ai-action-btn-disabled"
            if is_processing
            else "ai-action-btn ai-action-btn-primary"
        )
        generate_attrs = ' aria-disabled="true"' if is_processing else ""

        buttons = [
            format_html(
                '<a class="{}" href="{}"{}>生成</a>',
                generate_class,
                generate_url,
                generate_attrs,
            )
        ]
        if obj.result_file or obj.result_url:
            buttons.append(
                format_html(
                    '<a class="ai-action-btn ai-action-btn-success" href="{}">下载</a>',
                    download_url,
                )
            )
        return format_html("".join(buttons))

    def save_model(self, request: HttpRequest, obj, form, change) -> None:
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def generate_task_view(
        self, request: HttpRequest, object_id: str
    ) -> HttpResponseRedirect:
        if not self.has_change_permission(request):
            raise PermissionDenied
        task = get_object_or_404(self.model, pk=object_id)
        if task.status == AIGenerationTask.Status.PROCESSING:
            self.message_user(
                request, "任务正在生成中，请勿重复提交。", messages.WARNING
            )
        else:
            task.status = AIGenerationTask.Status.PENDING
            task.error_message = ""
            task.started_at = None
            task.completed_at = None
            task.save(
                update_fields=[
                    "status",
                    "error_message",
                    "started_at",
                    "completed_at",
                ]
            )
            execute_ai_generation_task.delay(task.pk)
            self.message_user(
                request, "生成任务已提交到 Celery 异步执行。", messages.INFO
            )
        return HttpResponseRedirect(
            reverse(f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist")
        )

    def download_result_view(
        self, request: HttpRequest, object_id: str
    ) -> HttpResponse | FileResponse:
        if not self.has_view_permission(request):
            raise PermissionDenied
        task = get_object_or_404(self.model, pk=object_id)
        if not task.result_file and task.result_url:
            try:
                download_result(task.pk)
            except (OSError, TimeoutError, ValueError) as exc:
                self.message_user(
                    request,
                    f"结果文件下载失败：{exc}",
                    messages.ERROR,
                )
                return HttpResponseRedirect(
                    reverse(
                        f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
                    )
                )
            task.refresh_from_db(fields=("result_file",))
        if not task.result_file:
            self.message_user(request, "没有可下载的结果文件。", messages.WARNING)
            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
                )
            )
        return FileResponse(
            task.result_file.open("rb"),
            as_attachment=True,
            filename=task.result_file.name.split("/")[-1],
        )

    @action(
        description="重新执行所选任务",
        icon="refresh",
        variant=ActionVariant.PRIMARY,
    )
    def retry_selected_tasks(self, request: HttpRequest, queryset) -> None:
        submitted = 0
        for task in queryset.filter(
            status__in=(
                AIGenerationTask.Status.FAILED,
                AIGenerationTask.Status.PENDING,
            )
        ):
            task.status = AIGenerationTask.Status.PENDING
            task.error_message = ""
            task.started_at = None
            task.completed_at = None
            task.save(
                update_fields=[
                    "status",
                    "error_message",
                    "started_at",
                    "completed_at",
                ]
            )
            execute_ai_generation_task.delay(task.pk)
            submitted += 1
        self.message_user(
            request,
            f"已重新提交 {submitted} 个任务。",
            messages.SUCCESS,
        )
