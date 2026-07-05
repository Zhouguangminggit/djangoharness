# 28 Cookiecutter 模板服务

## 目标

将 DjangoHarness 项目整理为 Cookiecutter 业务项目模板，使产品展示名称、英文技术短名、
副标题和作者可在生成时配置。

## 变更

- 新增 Cookiecutter 上下文、生成前校验和生成后占位符替换。
- 英文短名自动派生 Python 包名、Docker 镜像变量、Compose 项目名和数据库名。
- 产品页面、后台、邮件、文档、License 和部署配置改用模板参数。
- `agent-docs/` 与 `skill/` 保留 DjangoHarness 工程规范身份。
- 新增生成测试，覆盖有效项目生成、模板残留检查和非法英文短名拒绝。

## 验证记录

- `uv run pytest -q`（模板仓库）：通过，7 个测试全部通过。
- `uv lock --check`、`uv sync --all-groups --locked`（生成项目）：通过。
- `make format`、`make lint`、`make check`：通过；生成项目 100 个测试全部通过，
  存在 23 条上游依赖弃用警告。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无模型变更。
- `make docs-build`：通过，MkDocs 严格模式构建成功。
- `docker compose -f deploy/docker-compose.yml config`：通过；验证前从
  `.env.example` 创建本地 `.env`。

## 已知限制

- Logo、横幅、二维码和业务图片仍为占位资源，需要生成后人工替换。
- Cookiecutter 用于创建新项目，不负责合并模板更新到已经开发的项目。
