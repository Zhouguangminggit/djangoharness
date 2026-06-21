# 第十一批：模板与样式架构

## 问题

项目级 `templates/base.html` 和 `templates/home.html` 使用全局通用名称。由于项目模板目录优先于 app 模板目录，该结构容易覆盖 Django Admin、SimpleUI 和后续业务 app 的同名模板；首页同时仍展示脚手架默认内容。

## 完成内容

- 将项目布局迁移为 `layouts/application.html`，共享片段迁移到 `components/`。
- 将首页迁移到 `apps/core/templates/core/home.html`，URL 使用完整命名空间。
- 删除全局 `base.html` 和 `home.html`，认证模板改为继承语义化布局。
- 将单文件 CSS 拆分为 foundation、共享站点壳、首页和认证业务样式；认证脚本移入 accounts 静态命名空间。
- 重做 DjangoHarness 首页，并补充桌面、平板和移动端响应式规则。
- 增加模板来源测试，保证 SimpleUI Admin 模板不再被项目模板覆盖。
- 补充后续业务模块模板、CSS 和 JS 的目录规则。

## 验证结果

- 定向模板与认证测试：16 项通过。
- 静态资源查找：foundation、站点壳、首页、认证 CSS 和认证 JS 均可发现。
- `make format`：通过。
- `make lint`：通过。
- `make test`：18 项通过。
- `uv lock --check`：通过，解析 47 个包。
- `make check`：通过，18 项测试通过。
