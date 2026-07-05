# 第二十六批：AI 集成模块

## 目标

新增可复用的 AI 集成模块，支持后台管理员配置 AI 模型参数，并通过文字/图片提示词异步生成
视频（一期）、语音/3D 图像（预留）；任务状态在后台实时回显并带颜色区分。

## 变更清单

- 新增依赖：`volcengine-python-sdk[ark]`（`pyproject.toml` + `uv.lock`）。
- 新增环境变量：`.env.example` 增加 `AI_ENABLE_REAL_CALLS`、`AI_MEDIA_BASE_URL` 等 AI 相关配置。
- 新增 `apps/ai_integration/` 应用：
  - 模型：`AIModelConfig`、`AIGenerationTask`。
  - 迁移：`apps/ai_integration/migrations/0001_initial.py`。
  - 后台：`admin.py` 注册模型，列表显示带颜色状态、提示词摘要、操作列（生成/下载）和更多时间字段；支持「重新执行所选任务」。
  - 表单：`forms.py` 校验启用状态和当前支持的任务类型。
  - 自定义 admin view：`generate_task_view` 和 `download_result_view` 处理生成与下载。
  - 服务：`services.py` 封装火山方舟 SDK 创建、轮询、下载流程。
  - 任务：`tasks.py` 提供 Celery 异步入口。
- 项目集成：
  - `__PROJECT_PACKAGE__/settings/base.py` 注册应用并新增 `AI_*` 配置。
  - `__PROJECT_PACKAGE__/settings/admin.py` 在 Unfold 侧边栏新增「AI 集成」菜单。
- 新增 MySQL 8 参考 SQL：`db/ai_integration.sql`。
- 新增测试：`tests/test_ai_integration.py`，覆盖模型、服务、任务和 Admin。
- 新增文档：
  - `docs/ai-integration.md`（用户文档）
  - `agent-docs/ai-integration.md`（Agent 开发手册）
  - `docs/iterations/26-ai-integration.md`（本记录）

## 生成结果落盘修复

- 按火山方舟 SDK 实际响应结构从 `content.video_url` / `content.file_url` 提取结果地址，
  修复任务显示成功但 `result_url` 为空、Worker 不下载文件的问题。
- 生成成功后自动保存到 Django 默认文件存储；本地默认路径为
  `media/ai_results/<任务 ID>/`，不依赖 `AI_MEDIA_BASE_URL`。
- 后台对已有 `result_url` 但尚无 `result_file` 的任务也显示「下载」，点击后补充落盘，
  兼容修复前创建的历史任务。
- 支持本地真实图生视频调用：`DEBUG=True` 且未配置公网媒体地址时，参考图片自动转换为
  Base64 Data URL（上限 10 MB），无需配置生产域名。
- 更新 `mkdocs.yml` 导航和 `docs/framework/index.md` 框架能力卡片。

## 关键决策

- 优先使用脚本中的火山方舟 SDK，保持 API 调用方式一致；本地通过 `AI_ENABLE_REAL_CALLS=False`
  关闭真实调用，避免开发和测试依赖外部账号。
- 任务轮询在 Celery 任务内完成，间隔 3 秒，最大 10 分钟；失败后记录错误信息并允许后台重试。
- 不新增前台页面，模块保持可复用、不侵入业务主题。
- 语音和 3D 图像仅预留字段与枚举，默认仅实现视频生成。

## 验证结果

```bash
make format
make lint
make test
uv run python manage.py makemigrations --check --dry-run
make docs-build
uv lock --check
```

全部通过（测试结果：87 passed）。MkDocs 构建出现 Material 团队关于 MkDocs 2.0 的已知警告，
不属于本批次引入的错误。

## 遗留项

- 语音、3D 图像生成能力未实际实现。
- 未提供前台展示页面，业务主题可按需调用服务。
- 未接入对象存储，大文件下载依赖本地 `MEDIA_ROOT`。
