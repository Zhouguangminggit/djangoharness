import csv
import io
from dataclasses import dataclass

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import User

MAX_IMPORT_ROWS = 500
MAX_IMPORT_BYTES = 1024 * 1024
REQUIRED_COLUMNS = {"username", "email", "password"}


@dataclass(frozen=True)
class UserImportRow:
    username: str
    email: str
    password: str
    nickname: str = ""
    phone: str | None = None
    is_staff: bool = False
    is_active: bool = True


def parse_boolean(value: str, *, default: bool) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return default
    if normalized in {"1", "true", "yes", "y", "是"}:
        return True
    if normalized in {"0", "false", "no", "n", "否"}:
        return False
    raise ValidationError(f"无法识别布尔值“{value}”")


class BulkUserImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV 文件",
        help_text=(
            "UTF-8 编码，必填列：username、email、password；可选列："
            "nickname、phone、is_staff、is_active。单次最多 500 行。"
        ),
        widget=forms.ClearableFileInput(attrs={"accept": ".csv,text/csv"}),
    )

    rows: list[UserImportRow]

    def clean_csv_file(self):
        upload = self.cleaned_data["csv_file"]
        if upload.size > MAX_IMPORT_BYTES:
            raise ValidationError("CSV 文件不能超过 1MB。")
        try:
            text = upload.read().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValidationError("CSV 文件必须使用 UTF-8 编码。") from exc

        reader = csv.DictReader(io.StringIO(text))
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValidationError(f"缺少必填列：{', '.join(sorted(missing))}。")

        raw_rows = list(reader)
        if not raw_rows:
            raise ValidationError("CSV 文件中没有用户数据。")
        if len(raw_rows) > MAX_IMPORT_ROWS:
            raise ValidationError(f"单次最多导入 {MAX_IMPORT_ROWS} 个用户。")

        self.rows = []
        seen_usernames: set[str] = set()
        seen_emails: set[str] = set()
        seen_phones: set[str] = set()
        errors: list[str] = []
        for line_number, raw in enumerate(raw_rows, start=2):
            try:
                row = self._validate_row(raw, seen_usernames, seen_emails, seen_phones)
            except ValidationError as exc:
                errors.append(f"第 {line_number} 行：{'；'.join(exc.messages)}")
            else:
                self.rows.append(row)
        if errors:
            raise ValidationError(errors)
        return upload

    def _validate_row(
        self,
        raw: dict[str, str],
        seen_usernames: set[str],
        seen_emails: set[str],
        seen_phones: set[str],
    ) -> UserImportRow:
        username = (raw.get("username") or "").strip()
        email = User.objects.normalize_email((raw.get("email") or "").strip()).lower()
        password = raw.get("password") or ""
        nickname = (raw.get("nickname") or "").strip()
        phone = (raw.get("phone") or "").strip() or None
        errors: list[str] = []

        if not username:
            errors.append("用户名不能为空")
        if not email:
            errors.append("邮箱不能为空")
        if (
            username.lower() in seen_usernames
            or User.objects.filter(username__iexact=username).exists()
        ):
            errors.append("用户名已存在或在文件中重复")
        if email in seen_emails or User.objects.filter(email__iexact=email).exists():
            errors.append("邮箱已存在或在文件中重复")
        if phone and (
            phone in seen_phones or User.objects.filter(phone=phone).exists()
        ):
            errors.append("手机号已存在或在文件中重复")

        candidate = User(username=username, email=email, nickname=nickname, phone=phone)
        try:
            candidate.full_clean(exclude=("password",))
            password_validation.validate_password(password, candidate)
            is_staff = parse_boolean(raw.get("is_staff") or "", default=False)
            is_active = parse_boolean(raw.get("is_active") or "", default=True)
        except ValidationError as exc:
            errors.extend(exc.messages)
        if errors:
            raise ValidationError(errors)

        seen_usernames.add(username.lower())
        seen_emails.add(email)
        if phone:
            seen_phones.add(phone)
        return UserImportRow(
            username=username,
            email=email,
            password=password,
            nickname=nickname,
            phone=phone,
            is_staff=is_staff,
            is_active=is_active,
        )

    @transaction.atomic
    def save(self) -> list[User]:
        created = []
        for row in self.rows:
            created.append(
                User.objects.create_user(
                    username=row.username,
                    email=row.email,
                    password=row.password,
                    nickname=row.nickname,
                    phone=row.phone,
                    is_staff=row.is_staff,
                    is_active=row.is_active,
                )
            )
        return created
