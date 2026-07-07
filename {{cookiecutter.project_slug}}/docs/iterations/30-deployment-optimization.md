# 第三十批：部署优化

## 产出

- 部署 workflow 迁移到 `.github/workflows/`，新增质量检查与 GitHub Actions 自动部署流程。
- 新增 `make deploy-check`，支持本地提示型检查和生产严格检查。
- 生产 Docker 镜像切换到 Python 3.10 slim，Compose 仅保留 Web 与 Worker 应用服务。
- 移除 Compose 内置 MySQL、Redis 服务，生产数据库使用 RDS，Redis 使用宿主机或外部服务。
- 新增 `ensure_superuser` 管理命令，部署后按环境变量自动创建超级管理员，已存在则跳过。
- 部署文档统一到 `docs/deploy.md`，删除 `deploy/README.md`。

## 验证

本批应执行：

- `uv run pytest template_tests/test_cookiecutter_template.py -q`
- 生成项目后执行 `docker compose -f deploy/docker-compose.yml config`
- 生成项目后执行 `make deploy-check`
- `make format`
- `make lint`
- `make test`
- `make docs-build`
- `uv lock --check`

## 遗留事项

- 生产服务器必须预装 Docker Engine 与 Docker Compose plugin，并允许部署用户操作 Docker。
- `APP_ENV_VARS` 必须由 GitHub environment secrets 提供完整 `.env` 内容。
- 测试服务器可关闭 `USE_THIRD_PARTY_SERVICES`；生产启用时需补齐阿里云短信和邮件配置。
