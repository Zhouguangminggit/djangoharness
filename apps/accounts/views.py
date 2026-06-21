import json
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    LoginForm,
    NewPasswordForm,
    PasswordResetVerifyForm,
    PhoneRegisterForm,
    ProfileForm,
    ProfilePasswordChangeForm,
    RegisterForm,
)
from .services import (
    VerificationPurpose,
    VerificationRateLimited,
    request_verification_code,
)
from .tasks import send_welcome_email

User = get_user_model()
RESET_SESSION_KEY = "password_reset_grant"


def _safe_next(request: HttpRequest) -> str:
    target = request.POST.get("next") or request.GET.get("next") or ""
    if url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target
    return reverse("home")


def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if form.cleaned_data["remember_me"]:
            request.session.set_expiry(settings.AUTH_REMEMBER_SECONDS)
        else:
            request.session.set_expiry(0)
        return redirect(_safe_next(request))
    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": _safe_next(request), "media_page": "login"},
    )


def register(request: HttpRequest):
    mode = request.POST.get("mode") or request.GET.get("mode", "account")
    form_class = PhoneRegisterForm if mode == "phone" else RegisterForm
    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        if settings.USE_THIRD_PARTY_SERVICES:
            send_welcome_email.delay(user.username)
        login(request, user)
        messages.success(request, "注册成功")
        return redirect("home")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "mode": mode, "media_page": "register"},
    )


@login_required
def profile(request: HttpRequest):
    action = request.POST.get("action")
    profile_form = ProfileForm(
        request.POST if action == "profile" else None,
        request.FILES if action == "profile" else None,
        instance=request.user,
    )
    password_form = ProfilePasswordChangeForm(
        request.user,
        request.POST if action == "password" else None,
    )
    if request.method == "POST" and action == "profile" and profile_form.is_valid():
        profile_form.save()
        messages.success(request, "个人信息已更新")
        return redirect("accounts:profile")
    if request.method == "POST" and action == "password" and password_form.is_valid():
        user = password_form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "登录密码已修改")
        return redirect("accounts:profile")
    return render(
        request,
        "accounts/profile.html",
        {"profile_form": profile_form, "password_form": password_form},
    )


def password_reset(request: HttpRequest):
    form = PasswordResetVerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data["email"]).first()
        if user:
            request.session[RESET_SESSION_KEY] = {
                "user_id": user.pk,
                "expires": int(timezone.now().timestamp())
                + settings.AUTH_RESET_GRANT_SECONDS,
            }
            return redirect("accounts:password_reset_confirm")
        messages.info(request, "如果邮箱已注册，你可以继续完成密码重置")
    return render(
        request,
        "accounts/password_reset_form.html",
        {"form": form, "media_page": "password_reset"},
    )


def password_reset_confirm(request: HttpRequest):
    grant = request.session.get(RESET_SESSION_KEY)
    if (
        not isinstance(grant, dict)
        or grant.get("expires", 0) < timezone.now().timestamp()
    ):
        request.session.pop(RESET_SESSION_KEY, None)
        messages.error(request, "密码重置授权已失效，请重新验证")
        return redirect("accounts:password_reset")
    user_id = grant.get("user_id")
    if not isinstance(user_id, int):
        request.session.pop(RESET_SESSION_KEY, None)
        return redirect("accounts:password_reset")
    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user:
        request.session.pop(RESET_SESSION_KEY, None)
        return redirect("accounts:password_reset")
    form = NewPasswordForm(user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.session.pop(RESET_SESSION_KEY, None)
        return redirect("accounts:password_reset_complete")
    return render(
        request,
        "accounts/password_reset_confirm.html",
        {"form": form, "media_page": "password_reset"},
    )


def password_reset_complete(request: HttpRequest):
    return render(
        request,
        "accounts/password_reset_complete.html",
        {"media_page": "password_reset"},
    )


@require_POST
def logout_view(request: HttpRequest):
    logout(request)
    messages.success(request, "你已安全退出")
    return redirect("accounts:login")


def _json_payload(request: HttpRequest) -> dict[str, str]:
    if request.content_type == "application/json":
        try:
            value = json.loads(request.body)
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}
    return request.POST.dict()


@require_POST
def send_phone_code(request: HttpRequest) -> JsonResponse:
    phone = _json_payload(request).get("phone", "").strip()
    if not re.fullmatch(r"1\d{10}", phone):
        return JsonResponse({"ok": False, "message": "请输入有效手机号"}, status=400)
    if User.objects.filter(phone=phone).exists():
        return JsonResponse({"ok": True, "message": "验证码请求已受理"})
    return _send_code(VerificationPurpose.PHONE_REGISTER, phone)


@require_POST
def send_email_code(request: HttpRequest) -> JsonResponse:
    email = _json_payload(request).get("email", "").strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return JsonResponse({"ok": False, "message": "请输入有效邮箱"}, status=400)
    if not User.objects.filter(email__iexact=email, is_active=True).exists():
        return JsonResponse({"ok": True, "message": "验证码请求已受理"})
    return _send_code(VerificationPurpose.PASSWORD_RESET, email)


def _send_code(purpose: VerificationPurpose, target: str) -> JsonResponse:
    try:
        result = request_verification_code(purpose, target)
    except VerificationRateLimited as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=429)
    message = (
        "验证码请求已受理" if settings.USE_THIRD_PARTY_SERVICES else result.message
    )
    return JsonResponse({"ok": result.accepted, "message": message})
