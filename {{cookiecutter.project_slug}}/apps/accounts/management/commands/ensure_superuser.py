import os
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from loguru import logger


class Command(BaseCommand):
    help = "Create the deployment superuser from environment variables when absent."

    def handle(self, *args, **options) -> None:
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        phone = os.environ.get("DJANGO_SUPERUSER_PHONE", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        missing = [
            name
            for name, value in {
                "DJANGO_SUPERUSER_USERNAME": username,
                "DJANGO_SUPERUSER_EMAIL": email,
                "DJANGO_SUPERUSER_PASSWORD": password,
            }.items()
            if not value
        ]
        if missing:
            logger.info("跳过超级管理员初始化，缺少变量 names={}", ",".join(missing))
            self.stdout.write("跳过超级管理员初始化：缺少必要环境变量")
            return

        User = get_user_model()
        lookup = Q(username=username) | Q(email=email)
        if phone:
            lookup |= Q(phone=phone)
        if User.objects.filter(lookup).exists():
            logger.info("超级管理员已存在 username={} email={}", username, email)
            self.stdout.write("超级管理员已存在，跳过创建")
            return

        extra_fields: dict[str, Any] = {}
        if phone:
            extra_fields["phone"] = phone
            extra_fields["phone_verified"] = True
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )
        logger.info("超级管理员初始化完成 username={} email={}", username, email)
        self.stdout.write("超级管理员初始化完成")
