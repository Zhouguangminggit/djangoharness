# Windows 使用说明

## 环境准备

在 PowerShell 中安装 Python、uv 和 Git：

```powershell
winget install Python.Python.3.12
winget install astral-sh.uv
winget install Git.Git
python --version
uv --version
```

重新打开 PowerShell 使 PATH 生效。本地默认 SQLite，不运行 Celery 时无需安装 MySQL 和 Redis。

## 启动项目

```powershell
uv sync --all-groups
Copy-Item .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

Windows 默认没有 GNU Make，可直接运行对应命令：

```powershell
uv run ruff format apps base_framework celery_app tests manage.py
uv run ruff check apps base_framework celery_app tests manage.py
uv run mypy apps base_framework celery_app tests manage.py
uv run pytest
```

也可以通过 Git Bash 或 WSL 使用 `make format`、`make check`。

## Celery 与 Docker

原生 Windows 调试 Worker 使用兼容的 solo pool：

```powershell
uv run celery -A celery_app worker --loglevel=INFO --pool=solo
```

生产环境不要使用 solo pool。推荐安装 Docker Desktop 并使用完整服务：

```powershell
docker compose -f deploy/docker-compose.yml up --build
```

Docker Desktop 必须切换到 Linux containers。详细命令见 [Celery 使用说明](../celery/README.md)和 [Docker 部署说明](../../deploy/README.md)。
