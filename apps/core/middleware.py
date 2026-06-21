from __future__ import annotations

import re
import time
import uuid
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, HttpResponse
from loguru import logger

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _mask_username(username: str) -> str:
    if not username:
        return ""
    if "@" in username:
        local, domain = username.split("@", 1)
        return f"{local[:1]}***@{domain}"
    if username.isdigit() and len(username) >= 7:
        return f"{username[:3]}****{username[-4:]}"
    if len(username) <= 2:
        return f"{username[:1]}*"
    return f"{username[:1]}***{username[-1:]}"


def _request_context(request: HttpRequest) -> dict[str, Any]:
    supplied_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        supplied_request_id
        if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
        else uuid.uuid4().hex
    )
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        is_authenticated = True
        user_id = str(user.pk)
        username = user.get_username()
    else:
        is_authenticated = False
        user_id = "anonymous"
        username = ""

    return {
        "request_id": request_id,
        "user_id": user_id,
        "username": _mask_username(username),
        "is_authenticated": is_authenticated,
        "client_ip": request.META.get("REMOTE_ADDR", ""),
        "method": request.method,
        "path": request.path,
    }


class RequestLoggingMiddleware:
    """Attach safe request/user context and record request completion."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        context = _request_context(request)
        started_at = time.monotonic()

        with logger.contextualize(**context):
            try:
                response = self.get_response(request)
            except Exception:
                logger.exception("HTTP request failed")
                raise

            duration_ms = (time.monotonic() - started_at) * 1000
            status_code = response.status_code
            level = (
                "ERROR"
                if status_code >= 500
                else "WARNING"
                if status_code >= 400
                else "INFO"
            )
            logger.log(
                level,
                "HTTP request completed status_code={} duration_ms={:.2f}",
                status_code,
                duration_ms,
            )

        response["X-Request-ID"] = context["request_id"]
        return response
