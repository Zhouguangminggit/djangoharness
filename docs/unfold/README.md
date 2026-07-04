# Unfold 后台管理

项目使用 django-unfold 美化 Django Admin。Unfold 必须位于
`django.contrib.admin` 之前，项目内所有 `ModelAdmin` 必须继承
`unfold.admin.ModelAdmin`，否则表单仍会使用 Django 默认样式。

## 安装与兼容性

依赖统一由 uv 管理：

```bash
uv add "django-unfold>=0.74,<0.75"
```

项目保持 Python 3.10+ 和 Django 4.2。Unfold 0.99.x 要求 Python 3.12+ 和
Django 5.2+，因此当前使用兼容的 0.74 系列。升级 Unfold 前必须检查其 Python 和
Django 要求，并运行完整测试。

```python
INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
]
```

## 配置与菜单

后台品牌、主题、首页回调和侧边栏统一配置在
`base_framework/settings/admin.py` 的 `UNFOLD` 字典中。

- 侧栏需要同时显示图标和品牌文字时使用 `SITE_ICON`，不要配置只渲染图片的
  `SITE_LOGO`。
- 菜单链接使用 `reverse_lazy()` 和稳定的 Admin 命名路由，禁止硬编码路径。
- 菜单权限使用回调函数；隐藏菜单不能替代 Admin 视图自身的权限检查。
- 品牌静态资源通过 `static()` 回调解析，避免写死部署路径。
- 首页数据通过 `DASHBOARD_CALLBACK` 注入，不在模板中执行查询。

当前侧边栏包括数据概览、用户管理和消息通知。新增业务后台时，在业务 app 的
`admin.py` 注册模型，并按实际权限决定是否加入侧边栏。

## Admin 开发

普通模型后台使用：

```python
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(Example)
class ExampleAdmin(ModelAdmin):
    pass
```

自定义用户后台同时继承 Django `UserAdmin` 和 Unfold `ModelAdmin`，并使用 Unfold
提供的用户创建、修改和密码表单。Django 内置 Group Admin 也必须重新注册为
`BaseGroupAdmin + ModelAdmin`。批量操作使用 `unfold.decorators.action`；模型级入口放入
`actions_list`，选中记录的操作继续放入 `actions`。

自定义 Admin 页面必须使用 `admin_site.admin_view()` 或 Unfold action 的权限机制，
并继续执行模型级权限检查、CSRF 校验和输入验证。

## 模板与样式

- 自定义首页使用 `templates/admin/index.html`，继承 `admin/base.html`。
- Admin 专属资源放在 `static/admin/`，避免覆盖 Unfold 核心资源。
- 项目样式使用自身的语义类名和 Unfold CSS 变量，并同时验证浅色、深色和窄屏布局。
- 不引入项目级 Tailwind 构建链；自定义页面使用隔离的普通 CSS。

## 迁移和验证

旧主题的依赖、配置、模板类名和文档已移除。迁移或升级后台主题时至少执行：

```bash
uv lock --check
uv run python manage.py makemigrations --check --dry-run
make format
make lint
make test
make docs-build
make check
```

重点回归后台登录、菜单权限、数据看板、用户增删改、批量导入、Admin actions 和通知发布。
