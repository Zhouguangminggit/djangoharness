import re
import uuid

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    SetPasswordForm,
    UserCreationForm,
)

from .services import VerificationPurpose, verify_code

User = get_user_model()


class LoginForm(forms.Form):
    identifier = forms.CharField(label="账号", max_length=254)
    password = forms.CharField(label="密码", widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label="保持登录", required=False)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned = super().clean() or {}
        identifier = cleaned.get("identifier")
        password = cleaned.get("password")
        if identifier and password:
            self.user_cache = authenticate(
                self.request, username=identifier, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("账号或密码错误")
        return cleaned

    def get_user(self):
        return self.user_cache


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="邮箱")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("该邮箱已注册")
        return email


class PhoneRegisterForm(UserCreationForm):
    phone = forms.CharField(label="手机号", max_length=20)
    code = forms.CharField(label="验证码", min_length=4, max_length=8)

    class Meta:
        model = User
        fields = ("phone", "code", "password1", "password2")

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"1\d{10}", phone):
            raise forms.ValidationError("请输入有效的中国大陆手机号")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("该手机号已注册")
        return phone

    def clean(self):
        cleaned = super().clean() or {}
        phone, code = cleaned.get("phone"), cleaned.get("code")
        if (
            phone
            and code
            and not verify_code(VerificationPurpose.PHONE_REGISTER, phone, code)
        ):
            self.add_error("code", "验证码无效或已过期")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        user.username = f"mobile_{uuid.uuid4().hex[:12]}"
        user.email = f"{uuid.uuid4().hex}@mobile.djangoharness.invalid"
        if commit:
            user.save()
        return user


class PasswordResetVerifyForm(forms.Form):
    email = forms.EmailField(label="注册邮箱")
    code = forms.CharField(label="验证码", min_length=4, max_length=8)

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned = super().clean() or {}
        email, code = cleaned.get("email"), cleaned.get("code")
        if (
            email
            and code
            and not verify_code(VerificationPurpose.PASSWORD_RESET, email, code)
        ):
            self.add_error("code", "验证码无效或已过期")
        return cleaned


class NewPasswordForm(SetPasswordForm):
    pass


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="头像",
        required=False,
        help_text="支持 JPG、PNG、WebP，文件不超过 5MB。",
    )
    email = forms.EmailField(
        label="邮箱",
        required=False,
        help_text="可用于邮箱登录和找回密码。手机号注册用户可在此补充真实邮箱。",
    )
    phone = forms.CharField(
        label="手机号",
        required=False,
        disabled=True,
        help_text="手机号是已验证登录标识，暂不支持直接换绑。",
    )

    class Meta:
        model = User
        fields = ("avatar", "nickname", "username", "email", "phone")
        help_texts = {
            "nickname": "导航栏和欢迎信息优先显示昵称。",
            "username": "用户名可用于登录，修改后原用户名立即失效。",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_avatar_name = self.instance.avatar.name
        if self.instance.email.endswith("@mobile.djangoharness.invalid"):
            self.initial["email"] = ""

    def clean_nickname(self):
        return self.cleaned_data["nickname"].strip()

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if (
            User.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("该用户名已被使用")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            return self.instance.email
        if (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("该邮箱已被使用")
        return User.objects.normalize_email(email)

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        uploaded_avatar = self.files.get("avatar")
        if not uploaded_avatar:
            return avatar
        if (uploaded_avatar.size or 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("头像文件不能超过 5MB")
        content_type = getattr(uploaded_avatar, "content_type", "")
        if content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise forms.ValidationError("仅支持 JPG、PNG 或 WebP 图片")
        return avatar

    def save(self, commit=True):
        user = super().save(commit=commit)
        if (
            commit
            and "avatar" in self.changed_data
            and self._old_avatar_name
            and self._old_avatar_name != user.avatar.name
        ):
            user.avatar.storage.delete(self._old_avatar_name)
        return user


class ProfilePasswordChangeForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "旧密码不正确，请重新输入。",
    }
