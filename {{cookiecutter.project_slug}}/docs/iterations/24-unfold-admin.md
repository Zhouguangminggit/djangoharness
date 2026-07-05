# 第二十四批：Unfold 后台迁移

## 目标

使用 django-unfold 替换旧后台主题，同时保留用户管理、批量导入、通知发布、权限控制和
数据看板。

## 变更

- 依赖切换为 `django-unfold>=0.74,<0.75`。计划采用的 0.99 系列要求 Django 5.2
  和 Python 3.12，与项目 Django 4.2、Python 3.10+ 策略不兼容。
- 增加 Unfold 品牌、颜色、权限感知侧边栏和数据看板回调配置。
- 用户与通知后台接入 Unfold `ModelAdmin`；用户表单和 actions 使用 Unfold 接口。
- 批量新增改为 changelist action，保持原命名 URL、权限检查和原子导入行为。
- 后台首页、批量导入和 Admin 静态资源适配浅色、深色及响应式布局。
- 修正侧栏品牌区仅显示 Logo 的问题，补充站点标题、副标题和全局后台视觉细节。
- 按 Unfold 认证文档重新注册 Group Admin，确保用户与用户组页面均使用 Unfold 样式。
- 删除旧主题的现行配置和专题文档，补充 Unfold 用户文档及 Agent 开发规范。

## 验证结果

- `uv lock --check`：通过，解析 78 个包。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无模型变更。
- `make format`：通过，Python、Markdown 已格式化。
- `make lint`：通过，Ruff、mypy、Markdown 和 Django 检查均成功。
- `make test`：通过，62 项测试成功；保留 23 条第三方包弃用警告。
- `make docs-build`：通过，MkDocs 严格模式构建成功。
- `make check`：通过，完整静态检查和 62 项测试成功。

## 历史说明

早期迭代记录中的 SimpleUI 描述反映当时实现，现已由本批迁移取代，不再作为当前开发规范。
