# Django Admin 开发规则

- Unfold 品牌、菜单、首页和主题统一写在 `__PROJECT_PACKAGE__/settings/admin.py`；业务注册写在对应 app 的 `admin.py`。
- `unfold` 及启用的 contrib 位于 `django.contrib.admin` 之前，项目模型后台继承 `unfold.admin.ModelAdmin`。
- 默认启用 filters、forms、inlines 和 import_export；其他集成仅在业务实际使用并安装依赖时启用。
- 后台首页通过 `DASHBOARD_CALLBACK` 注入数据并优先使用 Unfold 原生组件，不依赖外部 CDN 展示核心信息。
- 内容和配置模型可使用 `ImportExportMixin`；密码、密钥或不可逆状态模型不得使用默认 Resource。导入先 dry-run 再原子提交。
- 批量动作使用 Unfold action，明确图标、文案和风险等级；危险操作保留确认、权限与当前用户保护。
- 测试首页权限和统计、增删改、筛选、批量操作、导入成功、重复数据回滚及无权访问。
