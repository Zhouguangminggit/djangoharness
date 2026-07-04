# 第二十三批：消息通知中心

## 目标

基于 `django-notifications-hq` 建立统一站内通知能力，支持后台人工发布、业务模块发送、
前台查询和已读状态管理。

## 变更

- 通过 uv 引入并配置 `django-notifications-hq`，新增项目通知适配层。
- 增加统一发送服务、后台发布记录、SimpleUI 发布入口和同步广播。
- 增加前台通知中心、页头未读数量、筛选分页和读状态操作。
- 增加模型 migration、MySQL 8 参考 SQL、业务文档和 Agent 开发规范。
- 增加服务、Admin、权限、模板及前台行为测试。

## 验证

实现完成后的实际命令结果记录于本节：

- `make format`：通过。
- `make lint`：通过，Ruff、mypy、Markdown 和 Django system check 均无错误。
- `make test`：通过，56 项测试全部通过；第三方通知包产生 23 条弃用警告。
- `make docs-build`：通过严格构建；MkDocs 报告历史迭代页面未加入导航的信息。
- `uv lock --check`：通过，共解析 78 个包。
- `make check`：通过。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无待生成迁移。

## 首版边界

仅提供同步站内通知，不包含删除、邮件、短信、推送、草稿、定时发布、动态人群、轮询或
WebSocket。广播规模产生明显请求延迟时，再迁移为具备幂等控制的 Celery 任务。
