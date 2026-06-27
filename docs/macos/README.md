# macOS 使用说明

## 环境准备

推荐使用 Homebrew 安装 Python、uv、MySQL 和 Redis：

```bash
xcode-select --install
brew install python@3.12 uv mysql redis
python3 --version
uv --version
```

只使用 SQLite 且不运行 Celery 时，可以不安装 MySQL 和 Redis。Apple Silicon 与 Intel Mac 使用相同项目命令。

## 启动项目

```bash
uv sync --all-groups
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

运行开发检查：

```bash
make format
make check
```

## 启动外部服务

```bash
brew services start mysql
brew services start redis
redis-cli ping
```

使用 MySQL 时修改 `.env` 中的 `DB_ENGINE` 和 `DB_*`。运行 Celery 的命令见 [Celery 使用说明](../celery/README.md)。

## Docker 方式

安装 Docker Desktop 后，从仓库根目录运行：

```bash
docker compose -f deploy/docker-compose.yml up --build
```

停止容器使用 `docker compose -f deploy/docker-compose.yml down`；不要添加 `-v`，除非确定要删除本地数据库数据。

