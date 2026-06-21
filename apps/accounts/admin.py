from typing import Any

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .admin_forms import BulkUserImportForm
from .models import User

admin.site.index_template = "admin/dashboard.html"
admin.site.site_header = "DjangoHarness 管理后台"
admin.site.site_title = "DjangoHarness 后台"
admin.site.index_title = "数据概览"


def configure_simpleui_action(
    action: Any, *, icon: str, action_type: str, confirm: str
) -> None:
    action.icon = icon
    action.type = action_type
    action.confirm = confirm


@admin.register(User)
class AccountsUserAdmin(UserAdmin):
    change_list_template = "admin/accounts/user/change_list.html"
    fieldsets = (
        (
            "基本信息",
            {
                "fields": ("username", "password"),
                "description": "管理用户的登录标识与密码状态。",
            },
        ),
        (
            "个人信息",
            {
                "fields": (
                    "avatar",
                    "nickname",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                ),
                "description": "维护用于识别、联系和展示的个人资料。",
            },
        ),
        (
            "权限",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "description": "控制后台访问、角色分组和细粒度权限。",
            },
        ),
        (
            "重要日期",
            {
                "fields": ("last_login", "date_joined"),
                "description": "系统记录的账号创建和最近登录时间。",
            },
        ),
    )
    add_fieldsets = (
        (
            "基本信息",
            {
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "password1",
                    "password2",
                ),
                "description": "设置登录账号、联系方式和初始密码。",
            },
        ),
        (
            "个人信息",
            {
                "fields": ("avatar", "nickname", "first_name", "last_name"),
                "description": "补充用户在系统中展示的个人资料。",
            },
        ),
        (
            "权限",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "description": "按需开放后台访问和业务操作权限。",
            },
        ),
    )
    list_display = (
        "avatar_preview",
        "username",
        "nickname",
        "email",
        "phone",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "nickname", "email", "phone")
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    ordering = ("-date_joined",)
    list_per_page = 20
    actions = ("activate_users", "deactivate_users")
    readonly_fields = ("last_login", "date_joined")

    class Media:
        css = {"all": ("admin/css/accounts-admin.css",)}

    @admin.display(description="头像")
    def avatar_preview(self, obj: User) -> str:
        if obj.avatar:
            return format_html(
                '<img class="accounts-avatar" src="{}" alt="" />', obj.avatar.url
            )
        initial = (obj.display_name or "U")[0].upper()
        return format_html('<span class="accounts-avatar-fallback">{}</span>', initial)

    @admin.action(description="启用所选用户")
    def activate_users(self, request: HttpRequest, queryset) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"已启用 {updated} 个用户。", messages.SUCCESS)

    configure_simpleui_action(
        activate_users,
        icon="fas fa-user-check",
        action_type="success",
        confirm="确定启用所选用户吗？",
    )

    @admin.action(description="停用所选用户")
    def deactivate_users(self, request: HttpRequest, queryset) -> None:
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(
            request,
            f"已停用 {updated} 个用户；当前登录账号不会被停用。",
            messages.WARNING,
        )

    configure_simpleui_action(
        deactivate_users,
        icon="fas fa-user-slash",
        action_type="warning",
        confirm="确定停用所选用户吗？",
    )

    def get_urls(self):
        return [
            path(
                "bulk-add/",
                self.admin_site.admin_view(self.bulk_add_view),
                name="accounts_user_bulk_add",
            )
        ] + super().get_urls()

    def bulk_add_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_add_permission(request):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        form = BulkUserImportForm(request.POST or None, request.FILES or None)
        if request.method == "POST" and form.is_valid():
            created = form.save()
            self.message_user(
                request, f"已成功新增 {len(created)} 个用户。", messages.SUCCESS
            )
            return redirect(reverse("admin:accounts_user_changelist"))

        context = {
            **self.admin_site.each_context(request),
            "title": "批量新增用户",
            "opts": self.model._meta,
            "form": form,
            "media": self.media + form.media,
            "has_view_permission": self.has_view_permission(request),
        }
        return TemplateResponse(request, "admin/accounts/user/bulk_add.html", context)
