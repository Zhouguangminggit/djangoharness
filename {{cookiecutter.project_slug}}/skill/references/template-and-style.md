# 模板与样式架构

## 模板命名空间

- `templates/layouts/` 放项目页面骨架，`templates/components/` 放跨业务共享片段。
- 业务页面放在 `apps/<app>/templates/<app>/`，引用时使用完整 `<app>/<page>.html`。
- 禁止在项目级模板目录创建 `base.html`、`home.html`、`login.html` 等全局通用名，避免覆盖 Admin、Unfold 和第三方 app。
- 业务页面默认继承 `layouts/application.html`；独立页面壳使用带业务语义的布局名。

## 静态资源分层

- `static/css/foundation.css`：设计令牌、重置和全局基础规则。
- `static/css/components/`：跨业务组件样式。
- `static/<app>/css/`、`static/<app>/js/`：业务页面样式和脚本。
- 页面通过 `extra_css`、`extra_js` 按需加载业务资源，类名使用页面或组件前缀。

新增模块时必须测试关键页面内容；涉及模板优先级时，使用 `get_template()` 断言模板 `origin`。

## Crispy Forms、导航与消息

- 使用 `apps.core.forms.BaseFormHelper` 或 `as_crispy_field` 统一表单结构；Helper 只负责布局，不改变字段、POST、CSRF 或验证。
- 默认使用 Bootstrap 5 模板包，产品样式由分层 CSS 提供，业务主题通过 Helper `css_class` 覆盖。
- 左侧品牌和右侧用户菜单固定，中间导航按业务替换；后台入口只对 staff 展示且后端继续鉴权。
- 菜单维护 `aria-expanded`，支持点击外部与 Esc 关闭；退出使用带 CSRF 的 POST。
- Django Messages 使用共享悬浮组件；success/info 可自动关闭，warning/error 默认保留。
