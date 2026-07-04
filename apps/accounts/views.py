import json
import re

from allauth.account.views import LoginView, LogoutView, SignupView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AccountSignupForm,
    NewPasswordForm,
    PasswordResetVerifyForm,
    PhoneRegisterForm,
    ProfileForm,
    ProfilePasswordChangeForm,
)
from .services import (
    VerificationPurpose,
    VerificationRateLimited,
    request_verification_code,
)
from .tasks import send_welcome_email

User = get_user_model()
RESET_SESSION_KEY = "password_reset_grant"


class AccountLoginView(LoginView):
    template_name = "account/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["media_page"] = "login"
        return context


class AccountSignupView(SignupView):
    template_name = "account/signup.html"

    def get_form_class(self):
        mode = self.request.POST.get("mode") or self.request.GET.get("mode", "account")
        return PhoneRegisterForm if mode == "phone" else AccountSignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.request.POST.get("mode") or self.request.GET.get(
            "mode", "account"
        )
        context["media_page"] = "register"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.user and settings.USE_THIRD_PARTY_SERVICES:
            send_welcome_email.delay(self.user.username)
        return response


class AccountLogoutView(LogoutView):
    template_name = "account/logout.html"
    http_method_names = ["post", "options"]

    def post(self, *args, **kwargs):
        response = super().post(*args, **kwargs)
        messages.success(self.request, "你已安全退出")
        return response


login_view = AccountLoginView.as_view()
register = AccountSignupView.as_view()
logout_view = AccountLogoutView.as_view()


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
