# 项目结构与配置

## 目录职责

- `apps/`：业务 Django app；通用能力放 `apps/core/`。
- `base_framework/`：URL、ASGI、WSGI 和分环境 settings。
- `celery_app/`：Celery 实例与自动发现配置。
- `templates/`、`static/`：项目级模板与静态资源；app 专属模板放入 app。
- `tests/`：跨模块和验收测试；简单单元测试也可放对应 app 的 `tests/`。
- `db/`：业务模型对应的 MySQL 8 SQL 参考定义。
- `docs/`：用户、工具和批次文档；`agent-docs/` 只存 Agent 规范。
- `deploy/`：生产 Dockerfile、Compose 服务和容器部署说明。

## 配置规则

- 公共配置写入 `base_framework/settings/base.py`，开发和生产差异分别写入 `dev.py`、`prod.py`。
- 密钥、域名、数据库和外部服务地址只能来自环境变量；新增变量必须同步 `.env.example`。
- 本地和测试默认使用 SQLite。MySQL、Redis 不应成为运行质量检查的前置条件。
- 不提交 `.env`、数据库文件、媒体文件、缓存或生成的静态资源。

## 新业务模块

新 app 放在 `apps/<business_name>/`，通过 AppConfig 注册到 `INSTALLED_APPS`。项目级 URL 只负责挂载 app URL，不直接承载业务视图。
