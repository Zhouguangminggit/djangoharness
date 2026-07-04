import pytest
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import Author, Category, Post, Tag
from apps.blog.services import (
    get_published_posts,
    get_related_posts,
    increment_view_count,
)

User = get_user_model()
PASSWORD = "Harness-test-password-2026"


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username="blog_admin", email="blog_admin@example.com", password=PASSWORD
    )
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=("is_staff", "is_superuser"))
    return user


@pytest.fixture
def category(db):
    return Category.objects.create(name="技术", slug="tech")


@pytest.fixture
def author(db):
    return Author.objects.create(name="测试作者", bio="作者简介")


@pytest.fixture
def published_post(db, category, author):
    return Post.objects.create(
        title="已发布文章",
        slug="published-post",
        category=category,
        author=author,
        summary="摘要",
        content_type=Post.ContentType.MARKDOWN,
        content_markdown="# 正文",
        status=Post.Status.PUBLISHED,
        published_at=timezone.now(),
    )


@pytest.fixture
def draft_post(db, category, author):
    return Post.objects.create(
        title="草稿文章",
        slug="draft-post",
        category=category,
        author=author,
        content_type=Post.ContentType.HTML,
        content_html="<p>草稿</p>",
        status=Post.Status.DRAFT,
    )


@pytest.mark.django_db
def test_post_absolute_url(published_post) -> None:
    assert published_post.get_absolute_url() == reverse(
        "blog:post_detail", kwargs={"slug": published_post.slug}
    )


@pytest.mark.django_db
def test_get_published_posts_excludes_drafts(draft_post, published_post) -> None:
    posts = list(get_published_posts())
    assert published_post in posts
    assert draft_post not in posts


@pytest.mark.django_db
def test_increment_view_count(published_post) -> None:
    assert published_post.view_count == 0
    new_count = increment_view_count(published_post.pk)
    assert new_count == 1
    published_post.refresh_from_db()
    assert published_post.view_count == 1


@pytest.mark.django_db
def test_get_related_posts_excludes_self(published_post, category, author) -> None:
    related = Post.objects.create(
        title="相关文章",
        slug="related-post",
        category=category,
        author=author,
        content_type=Post.ContentType.MARKDOWN,
        content_markdown="相关",
        status=Post.Status.PUBLISHED,
        published_at=timezone.now(),
    )
    result = list(get_related_posts(published_post))
    assert related in result
    assert published_post not in result


@pytest.mark.django_db
def test_anonymous_can_visit_post_list_and_detail(
    client: Client, published_post
) -> None:
    list_response = client.get(reverse("blog:post_list"))
    assert list_response.status_code == 200
    assert published_post.title in list_response.content.decode()

    detail_response = client.get(published_post.get_absolute_url())
    assert detail_response.status_code == 200
    assert published_post.title in detail_response.content.decode()


@pytest.mark.django_db
def test_draft_post_is_not_accessible(client: Client, draft_post) -> None:
    response = client.get(draft_post.get_absolute_url())
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_filter(client: Client, category, published_post) -> None:
    response = client.get(
        reverse("blog:category_posts", kwargs={"slug": category.slug})
    )
    assert response.status_code == 200
    assert published_post.title in response.content.decode()


@pytest.mark.django_db
def test_tag_filter(client: Client, published_post) -> None:
    tag = Tag.objects.create(name="Django", slug="django")
    published_post.tags.add(tag)

    response = client.get(reverse("blog:tag_detail", kwargs={"slug": tag.slug}))
    assert response.status_code == 200
    assert published_post.title in response.content.decode()


@pytest.mark.django_db
def test_category_list_page(client: Client, category) -> None:
    response = client.get(reverse("blog:category_list"))
    assert response.status_code == 200
    assert category.name in response.content.decode()


@pytest.mark.django_db
def test_admin_creates_post(client: Client, admin_user, category, author) -> None:
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:blog_post_add"),
        {
            "title": "后台创建的文章",
            "slug": "admin-post",
            "category": category.pk,
            "author": author.pk,
            "content_type": "markdown",
            "content_markdown": "# 内容",
            "status": "published",
            "published_at_0": "2026-01-01",
            "published_at_1": "00:00:00",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "_save": "保存",
        },
    )

    assert response.status_code == 302
    post = Post.objects.get(slug="admin-post")
    assert post.created_by == admin_user


@pytest.mark.django_db
def test_admin_post_form_validates_content_by_type(
    client: Client, admin_user, category, author
) -> None:
    client.force_login(admin_user)

    response = client.post(
        reverse("admin:blog_post_add"),
        {
            "title": "验证文章",
            "slug": "validate-post",
            "category": category.pk,
            "author": author.pk,
            "content_type": "markdown",
            "content_markdown": "",
            "status": "draft",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "_save": "保存",
        },
    )

    assert response.status_code == 200
    assert "必须填写 Markdown 内容" in response.content.decode()
    assert not Post.objects.filter(slug="validate-post").exists()


@pytest.mark.django_db
def test_header_has_blog_link_for_anonymous_user(client: Client) -> None:
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert reverse("blog:post_list") in response.content.decode()


@pytest.mark.django_db
def test_view_count_increments_on_detail_view(client: Client, published_post) -> None:
    client.get(published_post.get_absolute_url())
    published_post.refresh_from_db()
    assert published_post.view_count == 1


def test_blog_templates_use_project_namespace() -> None:
    template = get_template("blog/post_list.html")
    assert "apps/blog/templates" in str(getattr(template, "origin", ""))
