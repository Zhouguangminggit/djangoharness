# 模板与样式架构

## 模板命名空间

- `templates/layouts/` 只放项目级页面骨架，例如 `layouts/application.html`。
- `templates/components/` 只放跨业务共享的无业务状态片段，例如导航和消息提示。
- 业务页面放在 `apps/<app>/templates/<app>/`，引用时必须使用 `<app>/<page>.html`。
- 禁止在项目级 `templates/` 新增 `base.html`、`home.html`、`login.html` 等通用名称，避免优先级高于 Django Admin、SimpleUI 或第三方 app 的同名模板。
- 业务模板继承 `layouts/application.html`；需要完全不同页面壳时建立带语义的布局名，不复用通用 `base.html`。

## 样式分层

- `static/css/foundation.css` 保存设计令牌、重置和全局基础规则。
- `static/css/components/` 保存跨业务组件样式，不写具体页面布局。
- app 页面样式放在 `static/<app>/css/`，通过布局的 `extra_css` block 按需加载。
- app 脚本放在 `static/<app>/js/`，通过 `extra_js` block 按需加载；全站脚本放在 `static/js/`。
- CSS 类使用页面或组件前缀，避免 `.card`、`.title` 等无边界名称污染其他模块。

## 新模块模板

1. 创建 `apps/orders/templates/orders/list.html` 并继承 `layouts/application.html`。
1. 创建 `static/orders/css/list.css`，在页面的 `extra_css` block 引入。
1. URL 或视图使用完整模板名 `orders/list.html`。
1. 测试页面关键内容，并在模板优先级敏感时断言 `get_template()` 的 `origin`。
