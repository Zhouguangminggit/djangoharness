from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountsUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
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
                )
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
                )
            },
        ),
        ("重要日期", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "nickname",
                    "avatar",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = (
        "username",
        "nickname",
        "email",
        "phone",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "nickname", "email", "phone")
