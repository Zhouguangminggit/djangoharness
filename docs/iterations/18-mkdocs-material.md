# 第十八批：MkDocs + Material 文档站

## 产出

- 将 MkDocs Material 加入开发依赖并同步锁文件。
- 新增 Material 主题、中文搜索、深浅色模式、代码复制和文档导航配置。
- 新增文档首页以及 MkDocs 使用、写作、严格构建和静态部署说明。
- 增加 `docs-serve` 与 `docs-build` 命令，文档开发服务器使用 `8001` 端口。
- 更新 README 和 Agent 规范，明确业务文档目录、导航维护和验收要求。
- 忽略可重新生成的 `site/` 静态站点目录。
- 为文档站、开发环境、开发工具、框架能力和迭代记录增加独立概览页，避免
  `navigation.indexes` 将首篇业务文档提升后隐藏。
- 开启导航展开、面包屑、目录跟随、内容标签、搜索分享和社交链接，并增加首页卡片与主题
  样式。

## 验证

- `make format`：通过，Python 文件无需调整，Markdown 已格式化。
- `make lint`：通过，Ruff、mypy、mdformat 与 Django system check 均无错误。
- `make docs-build`：通过，严格模式成功生成文档站。
- 生成的 Windows 页面 HTML 已确认同时包含 `macOS` 与 `uv` 导航节点。
- `UV_CACHE_DIR=.uv-cache uv lock --check`：通过，解析 72 个包。
- `make test`：失败，38 项中 37 项通过；既有首页测试期望文案“把业务想法，
  落到可靠的工程底座上”，当前首页响应不包含该文案。
- `make check`：未通过；首次执行因两个既有 Markdown 文件未格式化而停止，格式化后仍受
  上述首页测试失败影响。

## 遗留项

无。
