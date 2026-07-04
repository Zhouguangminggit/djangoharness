# 博客模块 Agent 开发手册

## 模块定位

`apps/blog/` 是可复用的 CMS 式博客模块。不同业务主题可直接复用，也可在模型、Admin、
视图和模板中扩展。

## 核心模型

| 模型 | 作用 |
|------|------|
| `Category` | 文章分类，单级，预留 `parent` 扩展点 |
| `Tag` | 文章标签，多对多关联到 `Post` |
| `Author` | 前台作者，与 `User` 可选一对一关联 |
| `Post` | 文章主体，支持富文本或 Markdown |
| `PostImage` | 文章附图，通过内联管理 |

## 关键约定

- 所有图片上传使用 `apps.blog.models.ImageUploadTo`，生成 UUID 文件名并按日期分目录。
- 前台统一使用 `apps.blog.services.get_published_posts()` 获取可见文章。
- 阅读量通过 `increment_view_count()` 使用 `F()` 表达式原子递增。
- 富文本字段使用 `django_ckeditor_5.fields.CKEditor5Field`；上传路由挂载在 `/ckeditor5/`。

## 扩展点

### 新增字段

在 `apps/blog/models.py` 的 `Post` 中新增字段后，执行：

```bash
uv run python manage.py makemigrations
uv run python manage.py makemigrations --check --dry-run
```

并同步更新 `db/blog.sql`。

### 新增后台能力

- 继承 `unfold.admin.ModelAdmin`，业务后台注册写在 `apps/blog/admin.py`。
- Unfold 侧边栏菜单统一配置在 `base_framework/settings/admin.py`。新增博客模型后，
  需在该文件的 `UNFOLD["SIDEBAR"]["navigation"]` 中补充菜单项，并设置权限回调。
- 禁止在 Admin 中写死业务地址或密钥。

### 新增前台视图

- 视图写在 `apps/blog/views.py`。
- URL 写在 `apps/blog/urls.py`，设置 `app_name = "blog"`。
- 模板放在 `apps/blog/templates/blog/`，继承 `templates/layouts/application.html`。
- 静态资源放在 `static/blog/css/` 和 `static/blog/js/`，通过 `extra_css` / `extra_js` 加载。

### 修改内容渲染

Markdown 详情页使用 `markdown-it` CDN 在前端渲染，配置见 `static/blog/js/blog.js`。
如需后端渲染，可在模板中使用 `markdown` 过滤器，但需自行处理 XSS。

## 复用注意事项

- 不同业务主题若需要无限极分类，建议引入 `django-mptt` 并改造 `Category`。
- 若主题需要“用户即作者”，将 `Author.user` 设置为必填或自动创建。
- 若主题不需要 Markdown，可隐藏该字段；但建议保留模型字段以减少迁移冲突。
- 首页是否展示最新文章由业务主题自行决定，博客模块不耦合首页。
