from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from notifications.models import Notification


@login_required
def notification_list(request: HttpRequest) -> HttpResponse:
    status = request.GET.get("status", "all")
    queryset = Notification.objects.filter(recipient=request.user)
    if status == "unread":
        queryset = queryset.unread()
    elif status == "read":
        queryset = queryset.read()
    else:
        status = "all"

    page = Paginator(queryset, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "notifications_center/list.html",
        {"page": page, "status": status},
    )


def _user_notification(request: HttpRequest, notification_id: int) -> Notification:
    return get_object_or_404(Notification, pk=notification_id, recipient=request.user)


def _notification_redirect(request: HttpRequest) -> HttpResponse:
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("notifications_center:list")


@login_required
@require_POST
def mark_read(request: HttpRequest, notification_id: int) -> HttpResponse:
    _user_notification(request, notification_id).mark_as_read()
    return _notification_redirect(request)


@login_required
@require_POST
def mark_unread(request: HttpRequest, notification_id: int) -> HttpResponse:
    _user_notification(request, notification_id).mark_as_unread()
    return _notification_redirect(request)


@login_required
@require_POST
def mark_all_read(request: HttpRequest) -> HttpResponse:
    updated = Notification.objects.filter(recipient=request.user).mark_all_as_read()
    messages.success(request, f"已将 {updated} 条消息标记为已读。")
    return redirect("notifications_center:list")
