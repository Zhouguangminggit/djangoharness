# 部署说明

## 上线检测

部署前先复制并补齐 `.env`。生产环境必须配置：

- `DJANGO_SETTINGS_MODULE=__PROJECT_PACKAGE__.settings.prod`
- `DJANGO_SECRET_KEY`、`DJANGO_DEBUG=False`、`DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`，填写完整 HTTPS 来源
- `DB_ENGINE=mysql` 及 `DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`
- `CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND`、`AUTH_VERIFICATION_REDIS_URL`
- `DJANGO_SUPERUSER_USERNAME`、`DJANGO_SUPERUSER_EMAIL`、`DJANGO_SUPERUSER_PASSWORD`

可选服务按需启用。`USE_THIRD_PARTY_SERVICES=True` 时必须同时配置阿里云短信和邮件相关变量；
测试服务器可保持关闭，不会强制访问阿里云服务。AI、OSS、日志文件和媒体存储也以 `.env`
手工配置为准。

上线前执行：

```bash
make deploy-check
make lint
make test
make docs-build
uv lock --check
docker compose -f deploy/docker-compose.yml config
```

GitHub Actions 部署使用 `.github/workflows/deploy.yml`。在对应 environment 配置 secrets：

- ACR：`ACR_REGISTRY`、`ACR_NAMESPACE`、`ACR_REPO`、`ACR_USERNAME`、`ACR_PASSWORD`
- SSH：`DEPLOY_HOST`、`DEPLOY_PORT`、`DEPLOY_USER`、`DEPLOY_PATH`、`DEPLOY_SSH_PRIVATE_KEY`
- 应用配置：`APP_ENV_VARS`，内容为完整生产 `.env`

流水线会执行严格部署检查、质量门禁、镜像构建、推送阿里云 ACR、同步 Compose 和 `.env` 到服务器，
然后远端拉取镜像并重启服务。所有步骤日志带有 `[__PRODUCT_NAME__]` 前缀。

## 运维命令

服务器需预装 Docker Engine 和 Docker Compose plugin。MySQL 使用阿里云 RDS，Redis 使用宿主机或外部服务，
`deploy/docker-compose.yml` 不创建 MySQL、Redis 容器。

```bash
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs -f web worker
docker compose -f deploy/docker-compose.yml exec web python manage.py check --deploy
docker compose -f deploy/docker-compose.yml exec web python manage.py migrate --noinput
docker compose -f deploy/docker-compose.yml exec web python manage.py ensure_superuser
docker compose -f deploy/docker-compose.yml exec web python manage.py collectstatic --noinput
docker compose -f deploy/docker-compose.yml restart web worker
docker compose -f deploy/docker-compose.yml pull web worker
docker compose -f deploy/docker-compose.yml up -d --remove-orphans
```

快速定位日志：

```bash
docker compose -f deploy/docker-compose.yml logs --tail=200 web
docker compose -f deploy/docker-compose.yml logs --tail=200 worker
docker compose -f deploy/docker-compose.yml exec worker celery -A celery_app inspect active
```

普通更新不要执行 `down -v`。静态文件使用 `static_data` 卷，用户上传文件使用 `media_data` 卷；
生产环境应由反向代理、共享文件系统或对象存储提供 `/media/` 访问。

## 常见问题

- 部署检查失败：确认 `.env` 或 GitHub `APP_ENV_VARS` 包含必填变量；生产严格检查使用
  `DEPLOY_CHECK_ENV=production make deploy-check`。
- 数据库连接失败：确认 `DB_HOST` 指向 RDS 内网或公网地址，安全组允许服务器访问，`DB_ENGINE=mysql`。
- Redis 连接失败：生产不要使用容器内 `redis` 主机名，改为宿主机 IP、内网域名或托管 Redis 地址。
- 第三方服务报错：测试服务器可设置 `USE_THIRD_PARTY_SERVICES=False`；生产启用时补齐阿里云短信和邮件变量。
- 超级管理员未创建：确认 `DJANGO_SUPERUSER_USERNAME`、`DJANGO_SUPERUSER_EMAIL`、
  `DJANGO_SUPERUSER_PASSWORD` 已配置；同名、同邮箱或同手机号用户存在时命令会跳过。
- 健康检查失败：访问 `/health/`，并检查数据库连接、迁移状态、Gunicorn 日志和反向代理转发。
