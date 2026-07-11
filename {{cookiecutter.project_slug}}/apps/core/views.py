from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Report whether Django can reach its configured database."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "unhealthy"}, status=503)
    return JsonResponse({"status": "healthy"})


def product_introduction(request: HttpRequest):
    """Render the public, configuration-driven product introduction."""
    return render(request, "index.html")


@login_required
def application_home(request: HttpRequest):
    """Render the authenticated application landing page."""
    return render(request, "core/home.html")
