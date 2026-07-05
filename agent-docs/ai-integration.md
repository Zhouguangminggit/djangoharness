# AI 集成模块开发规范

## 范围

`apps/ai_integration` 负责对接第三方 AI 生成服务，提供可配置、可观察、可复用的异步生成能力。
业务主题需要视频/语音/3D 图像等 AI 生成能力时，应优先复用本模块，而不是为每个主题单独封装。

## 架构边界

- 模型：只放 `AIModelConfig` 和 `AIGenerationTask`，不耦合业务主题字段。
- 服务：`services.py` 封装第三方 SDK 调用；视图或 Admin 只调用服务函数，不直接调用 SDK。
- 任务：`tasks.py` 只负责调度边界，具体生成与轮询逻辑放在 `services.py`。
- 模板：本模块不强制提供前台模板，业务主题按需调用服务或复用 Admin 入口。

## 新增服务商

1. 在 `AIModelConfig.Provider` 增加枚举值。
1. 实现 `build_<provider>_client(config)` 工厂函数。
1. 在 `create_content_task` 和 `refresh_task_status` 中按 `provider` 分发。
1. 服务函数接收 `config_id` 或 `task_id`，不接收 ORM 对象作为 Celery 任务参数。

## 新增任务类型

1. 在 `AIGenerationTask.TaskType` 增加枚举值。
1. 实现对应类型的内容载荷构造函数。
1. 更新 `AIGenerationTaskAdminForm` 的校验规则。
1. 为新的任务类型补充单元测试，mock 对应的 SDK 调用。

## 配置与开关

- 密钥、base URL、模型 ID 必须来自环境变量或后台配置，禁止硬编码。
- `AI_ENABLE_REAL_CALLS` 默认 `False`，确保本地测试不访问真实 API。
- `AI_MEDIA_BASE_URL` 仅用于向第三方暴露上传的参考图片，不是生成结果存储配置。
  图生视频需要参考图片可被第三方服务公网访问：优先使用 `AI_MEDIA_BASE_URL`，
  未配置时回退到绝对地址形式的 `MEDIA_URL`。`DEBUG=True` 且两者都不可用时，
  自动把本地图片编码为 Base64 Data URL（限制 10 MB），支持本地真实调用。
  文生视频和结果落盘不依赖该配置。
- 第三方任务成功后，从 SDK 的 `content.video_url`（兼容 `content.file_url`）提取结果，
  并立即保存到 Django 默认文件存储；本地文件系统默认落在 `media/ai_results/`。
- 新增环境变量必须同步 `.env.example` 和 `docs/ai-integration.md`。

## Admin 交互约定

- 生成任务保存时只创建记录，不自动调用 AI 服务或投递 Celery 任务。
- 列表页通过 `operations` 显示「生成」与「下载」按钮：
  - 「生成」调用自定义 admin view，检查权限与当前状态后投递 Celery 任务。
  - 「下载」在 `result_file` 存在时返回 `FileResponse`；仅有 `result_url` 的历史任务
    会先补充下载到默认文件存储，再返回附件。
- 新增操作按钮时同步检查 `has_change_permission` / `has_view_permission`。

## 状态与日志

- 状态枚举必须同步模型、`services.py`、Admin 颜色映射和文档。
- 使用 `from loguru import logger` 记录关键状态；不记录 API Key 和完整提示词中的敏感信息。
- 失败原因写入 `AIGenerationTask.error_message`，便于后台排查。

## 测试

- 所有服务函数测试必须通过 mock SDK 完成，不依赖网络和真实账号。
- Celery 任务测试直接调用 `.run()` 并 mock `services.run_generation_workflow`。
- Admin 测试验证表单校验、权限、保存后是否投递 `.delay()`。

## 迁移与 SQL

- 模型变更后运行 `uv run python manage.py makemigrations`。
- 同步更新 `db/ai_integration.sql` 作为 MySQL 8 参考定义。
- 迁移是唯一执行源，SQL 不替代 migration。
