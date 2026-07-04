# 框架能力

框架在 Django 4.2 基础上提供异步任务、后台管理、认证、日志和生产部署约定。业务模块继续
遵循 Django app 边界，公共能力放入 `apps/core/`。

<div class="grid cards" markdown>

- :material-sync: **Celery**

  使用 Redis broker 执行可重试、尽量幂等的异步任务。

  [查看 Celery 指南](../celery/README.md)

- :material-view-dashboard-outline: **Unfold**

  提供现代化后台主题、权限感知菜单、数据看板和批量操作。

  [查看 Unfold 后台管理指南](../unfold/README.md)

- :material-account-key-outline: **用户认证**

  基于 django-allauth 提供用户名、邮箱和手机号认证，并保留可替换的验证码 Provider。

  [查看用户认证指南](../authentication.md)

- :material-shield-account-outline: **Agent 开发规范**

  Agent 规范保存在仓库 `agent-docs/` 中，约束架构、质量与交付流程。

  [在 GitHub 查看](https://github.com/Zhouguangminggit/djangoharness/tree/main/agent-docs)

</div>
