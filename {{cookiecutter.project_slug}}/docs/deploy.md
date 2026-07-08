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

GitHub Actions 部署使用 `.github/workflows/deploy.yml`。推送 `main` 分支会默认部署到
`production` environment，也可以手动运行 workflow 并选择 `production` 或 `staging`。
流水线会执行严格部署检查、质量门禁、镜像构建、推送阿里云 ACR、同步 Compose 和 `.env` 到服务器，
然后远端拉取镜像并重启服务。所有步骤日志带有 `[__PRODUCT_NAME__]` 前缀。

### GitHub environment

在仓库 `Settings -> Environments` 中创建部署环境。推荐至少创建：

| Environment | 用途 | 触发方式 | 配置建议 |
| --- | --- | --- | --- |
| `production` | 生产环境 | `main` 分支 push 或手动选择 | 配置生产 ACR、生产服务器 SSH、生产 `.env`；可开启审批保护 |
| `staging` | 测试环境 | 手动运行 workflow 并选择 `staging` | 可关闭第三方服务，使用测试服务器、测试数据库和测试 Redis |

每个 environment 下配置同名 secrets。这样测试和生产可以复用同一份 workflow，但使用不同服务器、
镜像仓库或 `.env` 内容。

### GitHub secrets

在目标 environment 的 `Secrets` 中配置：

| Secret | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `ACR_REGISTRY` | 是 | `registry.cn-hangzhou.aliyuncs.com` | 阿里云 ACR Registry 地址，不包含 namespace 和 repo |
| `ACR_NAMESPACE` | 是 | `my-team` | ACR 命名空间 |
| `ACR_REPO` | 是 | `__PROJECT_SLUG__` | ACR 镜像仓库名 |
| `ACR_USERNAME` | 是 | `deploy-user` | ACR 登录用户名，建议使用最小权限账号 |
| `ACR_PASSWORD` | 是 | `******` | ACR 登录密码或访问凭证 |
| `DEPLOY_HOST` | 是 | `192.0.2.10` | 目标服务器 IP 或域名 |
| `DEPLOY_PORT` | 是 | `22` | SSH 端口；未特殊配置时填 `22` |
| `DEPLOY_USER` | 是 | `deploy` | SSH 登录用户，需能执行 Docker 命令 |
| `DEPLOY_PATH` | 是 | `/opt/__PROJECT_SLUG__` | 服务器上的项目部署目录 |
| `DEPLOY_SSH_PRIVATE_KEY` | 是 | `-----BEGIN OPENSSH PRIVATE KEY-----...` | 与服务器公钥匹配的私钥，建议只授权部署用户 |
| `APP_ENV_VARS` | 是 | 多行 `.env` 内容 | 应用运行环境变量，workflow 会写入服务器 `${DEPLOY_PATH}/.env` |

workflow 会把镜像标记为 `${ACR_REGISTRY}/${ACR_NAMESPACE}/${ACR_REPO}:${GITHUB_SHA}`，并在同步到服务器的
`.env` 末尾追加 `__DOCKER_IMAGE_ENV__=<本次镜像地址>`，供 Compose 拉取本次构建产物。

### APP_ENV_VARS 内容

`APP_ENV_VARS` 是完整生产 `.env`，建议直接以多行 secret 保存。不要把反引号、Markdown 表格或额外说明写进
secret。推荐包含：

| Key | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | 是 | `__PROJECT_PACKAGE__.settings.prod` | 生产 settings 模块 |
| `DJANGO_SECRET_KEY` | 是 | `change-to-random-secret` | Django 密钥，必须使用强随机值 |
| `DJANGO_DEBUG` | 是 | `False` | 生产必须为 `False` |
| `DJANGO_ALLOWED_HOSTS` | 是 | `example.com,www.example.com` | 允许访问的域名，多个值用英文逗号分隔 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | 是 | `https://example.com,https://www.example.com` | 完整 HTTPS 来源，多个值用英文逗号分隔 |
| `DJANGO_TIME_ZONE` | 否 | `Asia/Shanghai` | 项目时区 |
| `DJANGO_HSTS_SECONDS` | 否 | `31536000` | HSTS 秒数；确认全站 HTTPS 后再设置较大值 |
| `DB_ENGINE` | 是 | `mysql` | 生产使用 MySQL |
| `DB_NAME` | 是 | `__DATABASE_NAME__` | RDS 数据库名 |
| `DB_USER` | 是 | `django_app` | RDS 应用账号 |
| `DB_PASSWORD` | 是 | `******` | RDS 应用账号密码 |
| `DB_HOST` | 是 | `rm-xxx.mysql.rds.aliyuncs.com` | RDS 内网或公网地址 |
| `DB_PORT` | 是 | `3306` | MySQL 端口 |
| `CELERY_BROKER_URL` | 是 | `redis://10.0.0.5:6379/0` | Celery broker Redis 地址 |
| `CELERY_RESULT_BACKEND` | 是 | `redis://10.0.0.5:6379/1` | Celery result backend Redis 地址 |
| `AUTH_VERIFICATION_REDIS_URL` | 是 | `redis://10.0.0.5:6379/2` | 验证码 Redis 地址，建议与 Celery DB 隔离 |
| `DJANGO_SUPERUSER_USERNAME` | 是 | `admin` | 部署初始化超级管理员用户名 |
| `DJANGO_SUPERUSER_EMAIL` | 是 | `admin@example.com` | 部署初始化超级管理员邮箱 |
| `DJANGO_SUPERUSER_PHONE` | 否 | `13800000000` | 部署初始化超级管理员手机号 |
| `DJANGO_SUPERUSER_PASSWORD` | 是 | `******` | 部署初始化超级管理员密码；用户已存在时不会覆盖 |
| `LOG_LEVEL` | 否 | `INFO` | 应用日志级别 |
| `LOG_FILE_ENABLED` | 否 | `True` | 是否启用容器内文件日志；启用时需考虑日志持久化 |
| `LOG_COLORIZE` | 否 | `False` | 日志采集器不支持 ANSI 颜色时设为 `False` |
| `USE_THIRD_PARTY_SERVICES` | 否 | `False` | 是否启用短信、邮件等第三方服务；测试服务器可关闭 |
| `ALIYUN_ACCESS_KEY_ID` | 条件必填 | `LTAI...` | `USE_THIRD_PARTY_SERVICES=True` 时必填 |
| `ALIYUN_ACCESS_KEY_SECRET` | 条件必填 | `******` | 阿里云 AccessKey Secret |
| `ALIYUN_SMS_SIGN_NAME` | 条件必填 | `示例签名` | 阿里云短信签名 |
| `ALIYUN_SMS_TEMPLATE_CODE` | 条件必填 | `SMS_123456789` | 阿里云短信模板 |
| `ALIYUN_EMAIL_ACCOUNT_NAME` | 条件必填 | `no-reply@example.com` | 阿里云邮件发信地址 |
| `AI_ENABLE_REAL_CALLS` | 否 | `False` | 是否启用真实 AI 调用 |
| `AI_VOLCANO_API_KEY` | 条件必填 | `******` | 启用火山方舟真实调用时填写 |

`APP_ENV_VARS` 示例：

```dotenv
DJANGO_SETTINGS_MODULE=__PROJECT_PACKAGE__.settings.prod
DJANGO_SECRET_KEY=replace-with-a-long-random-value
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DB_ENGINE=mysql
DB_NAME=__DATABASE_NAME__
DB_USER=django_app
DB_PASSWORD=replace-with-rds-password
DB_HOST=rm-xxx.mysql.rds.aliyuncs.com
DB_PORT=3306
CELERY_BROKER_URL=redis://10.0.0.5:6379/0
CELERY_RESULT_BACKEND=redis://10.0.0.5:6379/1
AUTH_VERIFICATION_REDIS_URL=redis://10.0.0.5:6379/2
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=replace-with-admin-password
USE_THIRD_PARTY_SERVICES=False
```

### 服务器要求

目标服务器需要预先准备：

| 项目 | 要求 |
| --- | --- |
| Docker | 已安装 Docker Engine |
| Docker Compose | 已安装 Compose plugin，可执行 `docker compose version` |
| SSH 用户 | `DEPLOY_USER` 能写入 `DEPLOY_PATH` 并执行 Docker 命令 |
| 部署目录 | `DEPLOY_PATH` 可不存在，workflow 会创建 `${DEPLOY_PATH}/deploy` |
| 网络 | 服务器能访问 ACR、RDS、Redis 和外部服务 |
| 反向代理 | 建议由 Nginx、SLB 或其它网关终止 HTTPS，并转发到 `${APP_PORT:-8000}` |

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
