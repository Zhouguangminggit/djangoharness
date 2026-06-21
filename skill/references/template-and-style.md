# 模板与样式架构

## 模板命名空间

- `templates/layouts/` 放项目页面骨架，`templates/components/` 放跨业务共享片段。
- 业务页面放在 `apps/<app>/templates/<app>/`，引用时使用完整 `<app>/<page>.html`。
- 禁止在项目级模板目录创建 `base.html`、`home.html`、`login.html` 等全局通用名，避免覆盖 Admin、SimpleUI 和第三方 app。
- 业务页面默认继承 `layouts/application.html`；独立页面壳使用带业务语义的布局名。

## 静态资源分层

- `static/css/foundation.css`：设计令牌、重置和全局基础规则。
- `static/css/components/`：跨业务组件样式。
- `static/<app>/css/`、`static/<app>/js/`：业务页面样式和脚本。
- 页面通过 `extra_css`、`extra_js` 按需加载业务资源，类名使用页面或组件前缀。

新增模块时必须测试关键页面内容；涉及模板优先级时，使用 `get_template()` 断言模板 `origin`。
