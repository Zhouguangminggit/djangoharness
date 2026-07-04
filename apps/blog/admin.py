from django.contrib import admin
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from .forms import PostAdminForm
from .models import Author, Category, Post, PostImage, Tag


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ("image", "caption", "sort_order")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_enabled", "sort_order", "created_at")
    list_filter = ("is_enabled",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "-created_at")


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_enabled", "created_at")
    list_filter = ("is_enabled",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ("name", "is_enabled", "email", "created_at")
    list_filter = ("is_enabled",)
    search_fields = ("name", "bio", "email")
    ordering = ("-created_at",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    form = PostAdminForm
    inlines = (PostImageInline,)
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "published_at",
        "is_top",
        "view_count",
    )
    list_filter = ("status", "category", "author", "is_top", "published_at")
    search_fields = ("title", "summary", "content_html", "content_markdown")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    ordering = ("-is_top", "-published_at", "-created_at")
    date_hierarchy = "published_at"
    list_per_page = 20

    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "author", "tags")}),
        (
            "内容",
            {
                "fields": (
                    "cover",
                    "summary",
                    "content_type",
                    "content_html",
                    "content_markdown",
                )
            },
        ),
        ("发布设置", {"fields": ("status", "is_top", "sort_order", "published_at")}),
        ("统计", {"fields": ("view_count", "created_by", "created_at", "updated_at")}),
    )
    readonly_fields = ("view_count", "created_by", "created_at", "updated_at")

    def save_model(self, request: HttpRequest, obj, form, change) -> None:
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
