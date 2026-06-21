import base64
import hashlib
import hmac
import json
import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class VerificationProvider(ABC):
    @abstractmethod
    def send(self, target: str, code: str) -> None: ...


def _quote(value: str) -> str:
    return quote(value, safe="~-._")


def _signed_aliyun_request(endpoint: str, params: dict[str, str]) -> None:
    common = {
        "AccessKeyId": settings.ALIYUN_ACCESS_KEY_ID,
        "Format": "JSON",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": secrets.token_hex(16),
        "SignatureVersion": "1.0",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Version": params.pop("Version"),
    }
    common.update(params)
    canonical = "&".join(
        f"{_quote(key)}={_quote(str(common[key]))}" for key in sorted(common)
    )
    to_sign = f"POST&%2F&{_quote(canonical)}"
    digest = hmac.new(
        f"{settings.ALIYUN_ACCESS_KEY_SECRET}&".encode(),
        to_sign.encode(),
        hashlib.sha1,
    ).digest()
    common["Signature"] = base64.b64encode(digest).decode()
    request = Request(
        endpoint,
        data=urlencode(common).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=settings.ALIYUN_REQUEST_TIMEOUT) as response:
        payload = json.loads(response.read())
    if payload.get("Code") not in {None, "OK"}:
        raise RuntimeError(f"阿里云发送失败：{payload.get('Code')}")


class AliyunSmsProvider(VerificationProvider):
    def send(self, target: str, code: str) -> None:
        _signed_aliyun_request(
            settings.ALIYUN_SMS_ENDPOINT,
            {
                "Version": "2017-05-25",
                "Action": "SendSms",
                "PhoneNumbers": target,
                "SignName": settings.ALIYUN_SMS_SIGN_NAME,
                "TemplateCode": settings.ALIYUN_SMS_TEMPLATE_CODE,
                "TemplateParam": json.dumps({"code": code}),
            },
        )


class AliyunEmailProvider(VerificationProvider):
    def send(self, target: str, code: str) -> None:
        _signed_aliyun_request(
            settings.ALIYUN_EMAIL_ENDPOINT,
            {
                "Version": "2015-11-23",
                "Action": "SingleSendMail",
                "AccountName": settings.ALIYUN_EMAIL_ACCOUNT_NAME,
                "AddressType": "1",
                "ReplyToAddress": "false",
                "ToAddress": target,
                "Subject": "DjangoHarness 密码重置验证码",
                "HtmlBody": f"<p>你的验证码是 <strong>{code}</strong>，请勿转发。</p>",
            },
        )


def provider_for(purpose: str) -> VerificationProvider:
    if purpose == "phone_register":
        return AliyunSmsProvider()
    if purpose == "password_reset":
        return AliyunEmailProvider()
    raise ValueError("不支持的验证码用途")
