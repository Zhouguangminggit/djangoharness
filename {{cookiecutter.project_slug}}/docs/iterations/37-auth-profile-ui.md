# 第三十七批：认证与个人中心 UI 优化

- 认证页面采用与产品介绍一致的明亮青绿色视觉，品牌媒体限制在装饰框内，不再放大铺满背景。
- 表单面板提升可用宽度；注册页桌面端双列、移动端单列，输入框、验证码按钮和提交按钮铺满可用空间。
- 个人中心改为全宽身份摘要和双栏编辑工作台，资料区与密码区充分利用大屏空间。
- 移除产品介绍页的 `<base>`，静态资源使用绝对路径，页内锚点不再错误跳到
  `/static/product-introduction/` 并触发目录索引 404。

## 验证结果

- 浏览器 1440 × 900 验收：注册表单宽 634px，两列字段各约 308px；个人中心内容区
  1384px，资料区 896px、安全区 464px，资料字段各约 403px，无横向溢出。
- `make format`：通过，生成项目中 1 个文件由 Ruff 机械格式化。
- `make lint`：通过，Ruff、格式、mypy、Markdown 与 Django check 均成功。
- `make test`：通过，103 项测试全部成功；第三方 notifications 包产生 23 条弃用警告。
- `make docs-build`：严格构建成功；MkDocs 仍提示既有未加入导航的历史迭代页面。
- `uv lock --check --offline`：通过，共解析 96 个包。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无迁移变化。
- `make check`：通过，103 项测试再次成功。
- `docker compose -f deploy/docker-compose.yml config --quiet`：通过。

首次在线 `uv sync` 因清华 PyPI 镜像请求 Hatchling 连续超时失败；随后使用相同锁文件和
本机缓存执行 `uv sync --offline` 成功，并完成全部门禁。
