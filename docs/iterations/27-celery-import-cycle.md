# 第二十七批：Celery 启动循环导入修复

## 问题

执行 `uv run celery -A celery_app worker --loglevel=INFO` 时，
`celery_app.celery` 导入 `base_framework.logging`，Python 随即执行
`base_framework/__init__.py`。该入口又反向导入尚未初始化完成的
`celery_app.celery.app`，因此触发循环导入。

## 变更

- 移除 `base_framework` 对 Celery 实例的反向导出，保持
  `celery_app -> base_framework.logging` 的单向依赖。
- 保留 `celery_app/__init__.py` 作为 `-A celery_app` 的唯一应用入口。
- 增加独立 Python 进程导入 Celery 应用的回归测试，避免测试进程的模块缓存掩盖问题。
- 补充启动前检查、入口职责和循环导入排查文档。

## 验证

- `uv run python -c "from celery_app.celery import app; print(app.main)"`：通过，输出
  `base_framework`。
- `uv run celery -A celery_app report`：通过，Celery CLI 正确加载应用和 Django 配置，
  未连接 broker。
- `uv run pytest tests/test_logging.py -q`：通过，5 项测试全部通过。
- `make lint`：通过，包含 Ruff、mypy、Markdown 和 Django 系统检查。
- `make test`：通过，88 项测试全部通过；存在 23 条来自第三方依赖的弃用警告。
- `UV_CACHE_DIR=.uv-cache uv lock --check`：通过，解析 91 个包。
- `make check`：通过。
