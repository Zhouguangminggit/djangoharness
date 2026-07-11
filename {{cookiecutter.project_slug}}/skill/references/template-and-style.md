# 模板与样式架构

## 模板命名空间

- `templates/layouts/` 只放项目级页面骨架，例如 `layouts/application.html`。
- `templates/components/` 只放跨业务共享的无业务状态片段，例如导航和消息提示。
- 业务页面放在 `apps/<app>/templates/<app>/`，引用时必须使用 `<app>/<page>.html`。
- 禁止在项目级 `templates/` 新增 `base.html`、`home.html`、`login.html` 等通用名称，避免优先级高于 Django Admin、Unfold 或第三方 app 的同名模板。
- 业务模板继承 `layouts/application.html`；需要完全不同页面壳时建立带语义的布局名，不复用通用 `base.html`。

## 样式分层

- `static/css/foundation.css` 保存设计令牌、重置和全局基础规则。
- `static/css/components/` 保存跨业务组件样式，不写具体页面布局。
- app 页面样式放在 `static/<app>/css/`，通过布局的 `extra_css` block 按需加载。
- app 脚本放在 `static/<app>/js/`，通过 `extra_js` block 按需加载；全站脚本放在 `static/js/`。
- CSS 类使用页面或组件前缀，避免 `.card`、`.title` 等无边界名称污染其他模块。

## Crispy Forms

- 业务表单使用 `apps.core.forms.BaseFormHelper` 或 `as_crispy_field` 统一错误、帮助文本和
  控件结构；表单仍负责校验，Helper 只负责布局。
- 默认模板包为 Bootstrap 5，但不依赖 Bootstrap 全站主题；站点 CSS 负责将模板包输出
  映射到产品设计令牌。业务主题通过 Helper 的 `css_class` 和业务静态文件覆盖。
- 上传、复选框、禁用字段、非字段错误和 formset 必须分别验收；不得因视觉迁移改变字段名、
  POST 协议、CSRF 或服务端验证。

## 新模块模板

1. 创建 `apps/orders/templates/orders/list.html` 并继承 `layouts/application.html`。
1. 创建 `static/orders/css/list.css`，在页面的 `extra_css` block 引入。
1. URL 或视图使用完整模板名 `orders/list.html`。
1. 测试页面关键内容，并在模板优先级敏感时断言 `get_template()` 的 `origin`。

## 全局导航与消息

- 左侧品牌和右侧用户菜单属于固定壳；中间导航按业务替换。后台入口只对 staff 展示，
  但可见性不能代替服务端 Admin 权限。
- 用户菜单和移动导航必须维护 `aria-expanded`，支持点击外部与 Esc 关闭；退出始终提交
  带 CSRF 的 POST 表单。
- Django Messages 使用共享悬浮组件；success/info 可自动关闭，warning/error 默认保留，
  所有级别均允许手动关闭并使用 `aria-live` 播报。
