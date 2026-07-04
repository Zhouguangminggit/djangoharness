from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Category, Post, Tag
from .services import (
    get_published_posts,
    get_related_posts,
    increment_view_count,
    is_post_published,
)


@require_GET
def post_list(request: HttpRequest, slug: str | None = None) -> HttpResponse:
    category = None
    queryset = get_published_posts()
    if slug:
        category = get_object_or_404(Category, slug=slug, is_enabled=True)
        queryset = queryset.filter(category=category)

    tag_slug = request.GET.get("tag")
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug, is_enabled=True)
        queryset = queryset.filter(tags=tag)
    else:
        tag = None

    paginator = Paginator(queryset, 12)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "blog/post_list.html",
        {"page": page, "category": category, "tag": tag},
    )


@require_GET
def post_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    if not is_post_published(post):
        return render(request, "blog/post_not_found.html", status=404)

    increment_view_count(post.pk)
    post.refresh_from_db()

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "related_posts": get_related_posts(post),
        },
    )


@require_GET
def category_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.filter(is_enabled=True).order_by(
        "sort_order", "-created_at"
    )
    return render(request, "blog/category_list.html", {"categories": categories})


@require_GET
def tag_detail(request: HttpRequest, slug: str) -> HttpResponse:
    tag = get_object_or_404(Tag, slug=slug, is_enabled=True)
    queryset = get_published_posts().filter(tags=tag)
    paginator = Paginator(queryset, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/tag_detail.html", {"tag": tag, "page": page})
