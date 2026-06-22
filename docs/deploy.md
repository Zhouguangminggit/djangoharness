# 上线配置说明

## 环境变量

- 设置 `DJANGO_DEBUG=False` 和安全随机的 `DJANGO_SECRET_KEY`。
- `DJANGO_ALLOWED_HOSTS` 填写线上域名，多个值使用逗号分隔。
- `DJANGO_CSRF_TRUSTED_ORIGINS` 填写完整 HTTPS 来源。
- 设置 `DB_ENGINE=mysql` 及 MySQL 8 的 `DB_*` 参数。
- 设置生产 Redis 的 `CELERY_BROKER_URL` 和 `CELERY_RESULT_BACKEND`。
- 设置 `AUTH_VERIFICATION_REDIS_URL`，验证码数据库应与 Celery 数据库隔离。
- 设置 `USE_THIRD_PARTY_SERVICES=True`，并配置阿里云 `ALIYUN_ACCESS_KEY_*`、短信签名、短信模板和邮件发信地址。
- 可通过 `AUTH_CODE_TTL`、`AUTH_CODE_COOLDOWN` 和 `AUTH_CODE_MAX_ATTEMPTS` 调整验证码安全策略。
- `USE_THREE_SERIVCE` 仅为旧拼写兼容项，新部署统一使用 `USE_THIRD_PARTY_SERVICES`。

## 发布检查

```bash
uv sync --frozen --no-dev
make check
DJANGO_SETTINGS_MODULE=base_framework.settings.prod uv run python manage.py migrate
DJANGO_SETTINGS_MODULE=base_framework.settings.prod uv run python manage.py collectstatic --noinput
```

生产 WSGI 入口为 `base_framework.wsgi:application`。容器部署使用 `deploy/Dockerfile` 和 `deploy/docker-compose.yml`，健康检查地址为 `/health/`，详细步骤见 [Docker 部署说明](../deploy/README.md)。HTTPS、媒体对象存储、日志采集和备份仍由部署环境负责。

生产环境不应关闭第三方验证码服务；若因受控验收临时关闭，必须同步限制站点访问范围并及时恢复。

用户头像位于 `MEDIA_ROOT`。生产环境必须将 `/media/` 交由反向代理、共享文件存储或对象存储提供访问，并对媒体卷执行持久化和备份；Django 仅在开发模式提供媒体文件。

手动运行 GitHub `production-deploy` workflow 前，需要在 `production` environment 配置 ACR、SSH、部署目录及 `APP_ENV_VARS` secrets。流水线会保留持久卷，更新失败时尝试恢复上一应用镜像；数据库 migration 仍需按版本设计可兼容的发布顺序。
