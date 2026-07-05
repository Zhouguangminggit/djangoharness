from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .admin_forms import BulkUserImportForm
from .models import User

admin.site.site_header = "__PRODUCT_NAME__ 管理后台"
admin.site.site_title = "__PRODUCT_NAME__ 后台"
admin.site.index_title = "数据概览"

if admin.site.is_registered(Group):
    admin.site.unregister(Group)


@admin.register(Group)
class AccountsGroupAdmin(BaseGroupAdmin, ModelAdmin):
    list_fullwidth = True
    search_fields = ("name",)


@admin.register(User)
class AccountsUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
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
    list_filter_submit = True
    list_fullwidth = True
    actions = ("activate_users", "deactivate_users")
    actions_list = ("bulk_add",)
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

    @action(
        description="启用所选用户",
        icon="person_check",
        variant=ActionVariant.SUCCESS,
    )
    def activate_users(self, request: HttpRequest, queryset) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"已启用 {updated} 个用户。", messages.SUCCESS)

    @action(
        description="停用所选用户",
        icon="person_off",
        variant=ActionVariant.WARNING,
    )
    def deactivate_users(self, request: HttpRequest, queryset) -> None:
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(
            request,
            f"已停用 {updated} 个用户；当前登录账号不会被停用。",
            messages.WARNING,
        )

    def has_bulk_add_permission(self, request: HttpRequest) -> bool:
        return self.has_add_permission(request)

    @action(
        description="批量新增",
        icon="group_add",
        permissions=("bulk_add",),
        url_path="bulk-add",
    )
    def bulk_add(self, request: HttpRequest) -> HttpResponse:
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
