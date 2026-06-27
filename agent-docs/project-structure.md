# 项目结构与配置

## 目录职责

- `apps/`：业务 Django app；通用能力放 `apps/core/`。
- `base_framework/`：URL、ASGI、WSGI 和分环境 settings。
- `celery_app/`：Celery 实例与自动发现配置。
- `templates/layouts/`、`templates/components/`：项目级布局与共享片段；禁止使用会覆盖第三方 app 的全局通用模板名。
- `apps/<app>/templates/<app>/`：业务模板命名空间；`static/<app>/`：业务页面样式与脚本。
- `static/css/`、`static/js/`：全站基础样式、共享组件和全站脚本。
- `tests/`：跨模块和验收测试；简单单元测试也可放对应 app 的 `tests/`。
- `db/`：业务模型对应的 MySQL 8 SQL 参考定义。
- `docs/`：MkDocs 文档源目录，存放用户、业务主题、工具和批次文档；新增可展示页面时同步
  更新 `mkdocs.yml` 的 `nav`。
- `mkdocs.yml`：Material 主题、站点导航、Markdown 扩展和严格构建配置。
- `site/`：MkDocs 生成的静态站点，属于可重新生成的忽略目录，不提交版本库。
- `agent-docs/`：只存 Agent 规范，不作为用户业务文档目录。
- `deploy/`：生产 Dockerfile、Compose 服务和容器部署说明。

## 配置规则

- 公共配置写入 `base_framework/settings/base.py`，开发和生产差异分别写入 `dev.py`、`prod.py`。
- 密钥、域名、数据库和外部服务地址只能来自环境变量；新增变量必须同步 `.env.example`。
- 本地和测试默认使用 SQLite。MySQL、Redis 不应成为运行质量检查的前置条件。
- 不提交 `.env`、数据库文件、媒体文件、缓存或生成的静态资源。

## 新业务模块

新 app 放在 `apps/<business_name>/`，通过 AppConfig 注册到 `INSTALLED_APPS`。项目级 URL 只负责挂载 app URL，不直接承载业务视图。
