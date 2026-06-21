from datetime import timedelta

from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.accounts.models import User

register = template.Library()


@register.simple_tag
def user_dashboard_data() -> dict[str, object]:
    now = timezone.now()
    month_start = (now.replace(day=1) - timedelta(days=155)).replace(day=1)
    monthly_rows = (
        User.objects.filter(date_joined__gte=month_start)
        .annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    monthly = {row["month"].strftime("%Y-%m"): row["total"] for row in monthly_rows}
    labels: list[str] = []
    cursor = month_start
    for _ in range(6):
        labels.append(cursor.strftime("%Y-%m"))
        cursor = (cursor + timedelta(days=32)).replace(day=1)

    total = User.objects.count()
    active = User.objects.filter(is_active=True).count()
    return {
        "summary": {
            "total": total,
            "active": active,
            "staff": User.objects.filter(is_staff=True).count(),
            "new_7_days": User.objects.filter(
                date_joined__gte=now - timedelta(days=7)
            ).count(),
        },
        "monthly": {
            "labels": labels,
            "values": [monthly.get(label, 0) for label in labels],
        },
        "status": {"active": active, "inactive": total - active},
    }
