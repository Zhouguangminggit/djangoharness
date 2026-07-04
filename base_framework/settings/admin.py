from django.templatetags.static import static
from django.urls import reverse_lazy


def admin_logo(_request):
    return static("accounts/brand/logo.png")


def admin_styles(_request):
    return static("admin/css/theme.css")


def can_manage_users(request):
    return request.user.has_perm("accounts.view_user")


def can_add_users(request):
    return request.user.has_perm("accounts.add_user")


def can_view_notifications(request):
    return request.user.has_perm("notifications_center.view_notificationpublication")


def can_publish_notifications(request):
    return request.user.has_perm("notifications_center.add_notificationpublication")


def can_view_blog_posts(request):
    return request.user.has_perm("blog.view_post")


def can_manage_blog_posts(request):
    return request.user.has_perm("blog.add_post")


UNFOLD = {
    "SITE_TITLE": "DjangoHarness 后台",
    "SITE_HEADER": "DjangoHarness",
    "SITE_SUBHEADER": "管理后台",
    "SITE_URL": "/",
    "SITE_ICON": admin_logo,
    "SITE_SYMBOL": "deployed_code",
    "STYLES": [admin_styles],
    "DASHBOARD_CALLBACK": "apps.accounts.admin_dashboard.dashboard_callback",
    "BORDER_RADIUS": "8px",
    "COLORS": {
        "primary": {
            "50": "oklch(97.3% .014 252)",
            "100": "oklch(94.3% .030 252)",
            "200": "oklch(88.5% .060 252)",
            "300": "oklch(79.5% .110 252)",
            "400": "oklch(68.5% .170 252)",
            "500": "oklch(58.5% .215 252)",
            "600": "oklch(49.5% .215 252)",
            "700": "oklch(42.5% .185 252)",
            "800": "oklch(36.5% .145 252)",
            "900": "oklch(31.5% .110 252)",
            "950": "oklch(22.5% .075 252)",
        }
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "工作台",
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": "数据概览",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    }
                ],
            },
            {
                "title": "用户管理",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "用户列表",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                        "permission": can_manage_users,
                    },
                    {
                        "title": "新增用户",
                        "icon": "person_add",
                        "link": reverse_lazy("admin:accounts_user_add"),
                        "permission": can_add_users,
                    },
                    {
                        "title": "批量新增",
                        "icon": "group_add",
                        "link": reverse_lazy("admin:accounts_user_bulk_add"),
                        "permission": can_add_users,
                    },
                ],
            },
            {
                "title": "消息通知",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "发布通知",
                        "icon": "send",
                        "link": reverse_lazy(
                            "admin:notifications_center_notificationpublication_add"
                        ),
                        "permission": can_publish_notifications,
                    },
                    {
                        "title": "发布记录",
                        "icon": "notifications",
                        "link": reverse_lazy(
                            "admin:notifications_center_notificationpublication_changelist"
                        ),
                        "permission": can_view_notifications,
                    },
                ],
            },
            {
                "title": "博客",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "发布文章",
                        "icon": "edit_note",
                        "link": reverse_lazy("admin:blog_post_add"),
                        "permission": can_manage_blog_posts,
                    },
                    {
                        "title": "文章列表",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                        "permission": can_view_blog_posts,
                    },
                    {
                        "title": "分类管理",
                        "icon": "folder",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                        "permission": can_view_blog_posts,
                    },
                    {
                        "title": "标签管理",
                        "icon": "tag",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                        "permission": can_view_blog_posts,
                    },
                    {
                        "title": "作者管理",
                        "icon": "person",
                        "link": reverse_lazy("admin:blog_author_changelist"),
                        "permission": can_view_blog_posts,
                    },
                ],
            },
        ],
    },
}
