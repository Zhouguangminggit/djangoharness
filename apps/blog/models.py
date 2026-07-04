import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


def _image_upload_path(prefix: str, filename: str) -> str:
    extension = Path(filename).suffix.lower() or ".jpg"
    today = uuid.uuid1().hex[:8]
    return f"blog/{prefix}/{today}/{uuid.uuid4().hex}{extension}"


class ImageUploadTo:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, instance, filename: str) -> str:
        return _image_upload_path(self.prefix, filename)

    def deconstruct(self):
        return ("apps.blog.models.ImageUploadTo", [self.prefix], {})


class Category(models.Model):
    name = models.CharField("名称", max_length=100)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    description = models.TextField("描述", blank=True)
    is_enabled = models.BooleanField("是否启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"
        indexes = [models.Index(fields=["slug", "is_enabled"])]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("blog:category_posts", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField("名称", max_length=50)
    slug = models.SlugField("Slug", max_length=50, unique=True)
    is_enabled = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "文章标签"
        verbose_name_plural = "文章标签"
        indexes = [models.Index(fields=["slug", "is_enabled"])]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("blog:tag_detail", kwargs={"slug": self.slug})


class Author(models.Model):
    name = models.CharField("显示名称", max_length=100)
    avatar = models.ImageField("头像", upload_to=ImageUploadTo("authors"), blank=True)
    bio = models.TextField("简介", blank=True)
    email = models.EmailField("邮箱", blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="关联账号",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="blog_author",
    )
    is_enabled = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "作者"
        verbose_name_plural = "作者"
        indexes = [models.Index(fields=["is_enabled"])]

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    class ContentType(models.TextChoices):
        HTML = "html", "富文本"
        MARKDOWN = "markdown", "Markdown"

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        ARCHIVED = "archived", "已归档"

    title = models.CharField("标题", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        verbose_name="分类",
        on_delete=models.PROTECT,
        related_name="posts",
    )
    author = models.ForeignKey(
        Author,
        verbose_name="作者",
        on_delete=models.PROTECT,
        related_name="posts",
    )
    cover = models.ImageField("封面图", upload_to=ImageUploadTo("covers"), blank=True)
    summary = models.TextField("摘要", blank=True)
    content_type = models.CharField(
        "内容格式",
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.HTML,
    )
    content_html = CKEditor5Field("富文本内容", blank=True, null=True)
    content_markdown = models.TextField("Markdown 内容", blank=True)
    tags = models.ManyToManyField(
        Tag, verbose_name="标签", blank=True, related_name="posts"
    )
    status = models.CharField(
        "状态", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_top = models.BooleanField("置顶", default=False)
    view_count = models.PositiveIntegerField("阅读量", default=0)
    sort_order = models.PositiveIntegerField("排序", default=0, blank=True)
    published_at = models.DateTimeField("发布时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_blog_posts",
    )

    class Meta:
        ordering = ("-is_top", "-published_at", "-created_at")
        verbose_name = "文章"
        verbose_name_plural = "文章"
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["category", "status", "published_at"]),
            models.Index(fields=["is_top", "published_at"]),
            models.Index(fields=["sort_order"]),
            models.Index(fields=["slug", "status"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:post_detail", kwargs={"slug": self.slug})


class PostImage(models.Model):
    post = models.ForeignKey(
        Post, verbose_name="文章", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField("图片", upload_to=ImageUploadTo("post_images"))
    caption = models.CharField("说明", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "-created_at")
        verbose_name = "文章附图"
        verbose_name_plural = "文章附图"

    def __str__(self) -> str:
        return f"{self.post.title} 的图片"
