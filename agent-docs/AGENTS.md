# DjangoHarness Agent 导航

DjangoHarness 是面向 AI 辅助开发的 Django 前后端不分离脚手架。修改代码前先读本页，随后只加载与任务相关的规范。

## 必读顺序

1. 阅读[项目结构与配置](project-structure.md)。
1. 按任务选择下方规范。
1. 开发结束执行“完成定义”。

## 任务入口

- Django 应用、模型、视图、表单、模板或静态资源：阅读 [Django 开发规范](django-development.md)。
- 测试、依赖、格式、类型或协作流程：阅读[工程质量规范](engineering-quality.md)。
- Celery 或 Redis：阅读[异步任务规范](async-tasks.md)。
- 模型、迁移或 SQL：阅读[数据库规范](database.md)。
- 用户、登录保护或验证码：阅读[用户认证规范](authentication.md)。
- 模板、页面布局或 CSS/JS：阅读[模板与样式架构](template-and-style.md)。
- Django Admin、SimpleUI、后台菜单或管理操作：阅读[后台管理规范](admin.md)。

## 完成定义

每批任务必须全部完成：

```bash
make format
make lint
make test
```

涉及业务模型时，同时提交 Django migration 和对应的 `db/*.sql`。在 `docs/iterations/` 新增或更新本批产出记录，写明变更、验证结果和遗留项。

## 当前批次

- [第一批：工程工具](../docs/iterations/01-tooling.md)
- [第二批：Agent 规范](../docs/iterations/02-agent-guidelines.md)
- [第三批：项目文档](../docs/iterations/03-documentation.md)
- [第四批：CI 与收口](../docs/iterations/04-ci-and-release.md)
- [第五批：跨平台与容器部署](../docs/iterations/05-platform-and-deployment.md)
- [第十批：认证验收](../docs/iterations/10-auth-acceptance.md)
