# 框架能力

框架在 Django 4.2 基础上提供异步任务、后台管理、认证、日志和生产部署约定。业务模块继续
遵循 Django app 边界，公共能力放入 `apps/core/`。

<div class="grid cards" markdown>

- :material-sync: **Celery**

  使用 Redis broker 执行可重试、尽量幂等的异步任务。

  [查看 Celery 指南](../celery/README.md)

- :material-view-dashboard-outline: **SimpleUI**

  定制后台模板、菜单和批量操作。

  [模板](../simpleui/template.md) · [菜单](../simpleui/menus.md) ·
  [Action](../simpleui/action.md)

- :material-shield-account-outline: **Agent 开发规范**

  Agent 规范保存在仓库 `agent-docs/` 中，约束架构、质量与交付流程。

  [在 GitHub 查看](https://github.com/Zhouguangminggit/djangoharness/tree/main/agent-docs)

</div>
