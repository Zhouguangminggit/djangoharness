from datetime import datetime

from django.db.models import F, QuerySet
from django.utils import timezone

from .models import Post


def get_published_posts() -> QuerySet[Post]:
    """返回前台可见的已发布文章查询集。"""
    return (
        Post.objects.filter(
            status=Post.Status.PUBLISHED, published_at__lte=timezone.now()
        )
        .select_related("category", "author")
        .prefetch_related("tags")
    )


def increment_view_count(post_pk: int) -> int:
    """使用 F() 表达式原子递增阅读量，返回更新后的数量。"""
    Post.objects.filter(pk=post_pk).update(view_count=F("view_count") + 1)
    return Post.objects.values_list("view_count", flat=True).get(pk=post_pk)


def get_related_posts(post: Post, limit: int = 4) -> QuerySet[Post]:
    """获取同分类的已发布相关文章，排除当前文章。"""
    return (
        get_published_posts()
        .filter(category=post.category)
        .exclude(pk=post.pk)
        .order_by("-is_top", "-published_at")[:limit]
    )


def is_post_published(post: Post) -> bool:
    """判断文章是否已在前台发布。"""
    return (
        post.status == Post.Status.PUBLISHED
        and post.published_at is not None
        and post.published_at <= datetime.now(tz=timezone.get_current_timezone())
    )
