from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "slug",
            "category",
            "author",
            "tags",
            "cover",
            "summary",
            "content_type",
            "content_html",
            "content_markdown",
            "status",
            "is_top",
            "sort_order",
            "published_at",
        )

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        content_type = cleaned.get("content_type")
        content_html = cleaned.get("content_html")
        content_markdown = cleaned.get("content_markdown")

        if content_type == Post.ContentType.HTML and not content_html:
            self.add_error("content_html", "富文本模式下必须填写富文本内容。")
        elif content_type == Post.ContentType.MARKDOWN and not content_markdown:
            self.add_error(
                "content_markdown", "Markdown 模式下必须填写 Markdown 内容。"
            )

        return cleaned

    def clean_slug(self) -> str:
        slug = self.cleaned_data["slug"]
        if " " in slug:
            raise ValidationError("Slug 不能包含空格。")
        return slug
