# Celery 使用说明

## 是什么

Celery 是异步任务队列。本项目使用 Redis 作为 broker 和结果后端，适合处理邮件、通知和不应阻塞 Web 请求的耗时操作。

## 准备配置

启动 Redis，并检查 `.env`：

```dotenv
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

验证 Redis：

```bash
redis-cli ping  # 应返回 PONG
```

## 启动 Worker

```bash
# Linux 和 macOS
uv run celery -A celery_app worker --loglevel=INFO

# 指定并发数和队列
uv run celery -A celery_app worker --loglevel=INFO --concurrency=4 --queues=celery

# Windows 本地调试
uv run celery -A celery_app worker --loglevel=INFO --pool=solo
```

Windows 的 solo pool 只用于开发调试，生产 Worker 应运行在 Linux 容器或主机上。

## 调用和验证任务

注册用户会通过 `.delay()` 触发欢迎任务。也可在 Django shell 中调用：

```bash
# 同步调用，不需要 Redis，适合调试业务逻辑
uv run python manage.py shell -c \
  "from apps.accounts.tasks import send_welcome_email; print(send_welcome_email.run('Ada'))"

# 异步投递，需要 Redis 和 Worker
uv run python manage.py shell -c \
  "from apps.accounts.tasks import send_welcome_email; print(send_welcome_email.delay('Ada').id)"
```

## 常用监控命令

```bash
uv run celery -A celery_app status             # 在线 Worker
uv run celery -A celery_app inspect ping       # 连通性
uv run celery -A celery_app inspect stats      # Worker 统计
uv run celery -A celery_app inspect active     # 正在执行
uv run celery -A celery_app inspect reserved   # 已预取等待执行
uv run celery -A celery_app inspect scheduled  # ETA/倒计时任务
uv run celery -A celery_app inspect registered # 已注册任务
uv run celery -A celery_app report             # 环境与配置报告
```

## 定时任务和控制命令

项目增加 `CELERY_BEAT_SCHEDULE` 后，可启动调度器：

```bash
uv run celery -A celery_app beat --loglevel=INFO
```

开发环境可以发送优雅关闭或清空队列命令：

```bash
uv run celery -A celery_app control shutdown
uv run celery -A celery_app purge  # 危险：永久删除队列中所有待处理任务
```

生产环境执行 `purge` 前必须确认队列和影响范围。正常停止优先向 Worker 进程发送 `TERM`，等待当前任务结束。

## Docker Compose

```bash
docker compose -f deploy/docker-compose.yml up -d redis worker
docker compose -f deploy/docker-compose.yml logs -f worker
docker compose -f deploy/docker-compose.yml exec worker celery -A celery_app inspect active
docker compose -f deploy/docker-compose.yml restart worker
```

## 常见问题

- `Connection refused`：检查 Redis 是否启动，以及容器内地址是否使用 `redis` 而非 `localhost`。
- `Received unregistered task`：确认任务使用 `@shared_task`，app 已注册，并重启 Worker。
- 任务一直 pending：确认 Worker 在线、监听了正确队列，并检查 Worker 日志。
- 任务重复执行：将业务操作设计为幂等，并为外部写入增加唯一键或状态检查。
- Windows Worker 异常：使用 `--pool=solo`，或改用 Docker Desktop/WSL。

任务参数、重试、幂等性与日志规则见 [异步任务规范](../../agent-docs/async-tasks.md)。
