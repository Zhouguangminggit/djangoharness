# 第二十五批：博客模块

## 目标

新增可复用的 CMS 式博客模块，支持后台配置分类、作者、文章和附图，前台无需登录即可
浏览，同时支持富文本、Markdown 和多图片上传。

## 变更清单

- 新增 `apps/blog/` 应用，包含：
  - 模型：`Category`、`Tag`、`Author`、`Post`、`PostImage`。
  - 迁移：`apps/blog/migrations/0001_initial.py`。
  - 后台：`apps/blog/admin.py` 注册模型；`__PROJECT_PACKAGE__/settings/admin.py` 在 Unfold 侧边栏新增“博客”菜单（发布文章、文章列表、分类、标签、作者）。
  - 表单：`apps/blog/forms.py`，校验内容格式与对应字段。
  - 服务：`apps/blog/services.py`，统一已发布查询集与阅读量递增。
  - 视图与模板：`post_list`、`post_detail`、`category_list`、`tag_detail` 及对应模板。
  - 静态资源：`static/blog/css/blog.css`、`static/blog/js/blog.js`。
- 新增依赖：`django-ckeditor-5`、`Markdown`（`pyproject.toml` + `uv.lock`）。
- 新增 CKEditor 5 配置：`__PROJECT_PACKAGE__/settings/base.py`。
- 挂载博客 URL 和 CKEditor 5 上传路由：`__PROJECT_PACKAGE__/urls.py`。
- 页头新增“博客”入口：`templates/components/site_header.html`。
- 新增 MySQL 8 参考 SQL：`db/blog.sql`。
- 新增测试：`tests/test_blog.py`，覆盖模型、服务、视图和 Admin。
- 新增文档：
  - `docs/blog.md`（用户文档）
  - `agent-docs/blog.md`（Agent 开发手册）
  - `docs/iterations/25-blog-module.md`（本记录）
- 更新 `mkdocs.yml` 导航，将博客模块加入“框架能力”。

## 关键决策

- 分类采用单级实现，预留 `parent` 字段便于后续扩展树形结构。
- 富文本使用 CKEditor 5，Markdown 前台使用 `markdown-it` 渲染。
- 作者模型与后台用户解耦，便于不同业务主题自定义作者展示信息。
- 首页不耦合最新文章区块，由业务主题按需决定。

## 验证结果

```bash
make format
make lint
make test
make docs-build
uv lock --check
```

全部通过（测试结果：76 passed）。

## 遗留项

- 未实现评论、点赞、订阅、SEO 元标签、定时发布、全文搜索和多语言。
- 大量图片上传或大流量场景下，可考虑将图片迁移到对象存储并接入 CDN。
