# Docker 部署说明

## 文件职责

- `Dockerfile`：多阶段生产镜像，使用 Python 3.12、uv、Gunicorn 和非 root 用户。
- `Dockerfile.dockerignore`：因为构建上下文是仓库根目录，使用 Dockerfile 专属忽略文件。
- `docker-compose.yml`：提供 Web、Celery Worker、MySQL 8 和 Redis 服务。

## 本地启动

先复制环境变量并至少设置安全的 `DJANGO_SECRET_KEY`、`MYSQL_APP_PASSWORD` 和 `MYSQL_ROOT_PASSWORD`：

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml up --build -d
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs -f web worker
```

访问 <http://127.0.0.1:8000/>，健康检查为 <http://127.0.0.1:8000/health/>。

## 常用运维命令

```bash
docker compose -f deploy/docker-compose.yml exec web python manage.py createsuperuser
docker compose -f deploy/docker-compose.yml exec web python manage.py migrate
docker compose -f deploy/docker-compose.yml restart web worker
docker compose -f deploy/docker-compose.yml down
```

数据存储在 Compose volumes。普通更新不要执行 `down -v`，该参数会删除 MySQL、Redis、静态和媒体数据卷。

用户头像保存在 `media_data` 持久卷。生产反向代理需要将 `/media/` 映射到该卷，或将 Django 存储后端替换为对象存储；不要通过 Gunicorn 长期直接提供媒体文件。

## 使用已发布镜像

```bash
DJANGOHARNESS_IMAGE=registry.example.com/team/djangoharness:tag \
  docker compose -f deploy/docker-compose.yml pull web worker
DJANGOHARNESS_IMAGE=registry.example.com/team/djangoharness:tag \
  docker compose -f deploy/docker-compose.yml up -d --remove-orphans
```

生产环境应在 `.env` 设置 `DJANGO_DEBUG=False`、域名、CSRF 来源、MySQL 和 Redis 参数，并由反向代理终止 HTTPS。Compose 使用 `MYSQL_APP_USER`、`MYSQL_APP_PASSWORD` 创建应用用户，不要把应用用户设置为 root。

## GitHub 生产部署

`production-deploy` workflow 需要在 GitHub `production` environment 配置：

- ACR：`ACR_REGISTRY`、`ACR_NAMESPACE`、`ACR_REPO`、`ACR_USERNAME`、`ACR_PASSWORD`。
- SSH：`DEPLOY_HOST`、`DEPLOY_PORT`、`DEPLOY_USER`、`DEPLOY_PATH`、`DEPLOY_SSH_PRIVATE_KEY`。
- 应用配置：`APP_ENV_VARS`，内容为完整生产 `.env`，不要把 `DJANGOHARNESS_IMAGE` 写入该 secret。

流水线只支持手动触发。它会先执行质量门禁，按 Git SHA 构建镜像，将 Compose 文件同步至服务器，然后无损更新服务。目标 Linux 主机必须预装 Docker Engine、Docker Compose plugin 和 `base64`，并允许部署用户操作 Docker。
