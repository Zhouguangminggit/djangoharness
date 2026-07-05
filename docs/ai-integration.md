# AI 集成

AI 集成模块为 DjangoHarness 提供可复用的第三方 AI 生成能力。管理员在后台配置模型参数后，
即可通过文字提示词和可选参考图片异步生成视频、语音或 3D 图像等内容。

## 安装与配置

依赖由 uv 统一管理，已包含火山方舟 SDK。首次部署执行常规迁移：

```bash
uv run python manage.py migrate
```

在 `.env` 中配置火山方舟相关参数：

```dotenv
AI_ENABLE_REAL_CALLS=False
AI_DEFAULT_PROVIDER=volcano_ark
AI_VOLCANO_API_KEY=your-api-key
AI_VOLCANO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
AI_VOLCANO_DEFAULT_MODEL=doubao-seedance-1-5-pro-251215
# 仅生产环境上传参考图片且 MEDIA_URL 不是公网地址时需要配置。
# 本地文生视频及生成结果落盘不需要此配置。
AI_MEDIA_BASE_URL=
AI_TASK_POLL_INTERVAL_SECONDS=3
AI_TASK_MAX_POLL_SECONDS=600
```

`AI_ENABLE_REAL_CALLS=False` 时，系统不会真正调用第三方 API，而会生成 mock 结果文件并
保存到 `MEDIA_ROOT/ai_results/<任务 ID>/`，便于本地开发、后台下载及其他模块引用。

!!! note "参考图片的公开访问"

```
`AI_MEDIA_BASE_URL` 只用于把本系统上传的参考图片提供给第三方服务，不控制生成结果
保存位置。本地开发（`DEBUG=True`）进行真实图生视频调用时，系统会自动把本地参考图片
编码为 Base64 Data URL，不需要配置公网域名。生产环境应配置 `AI_MEDIA_BASE_URL`
或使用绝对地址形式的 `MEDIA_URL`，避免把较大的图片编码进 API 请求。

生成结果始终由 Worker 自动下载到 Django 默认文件存储，本地默认是
`media/ai_results/`。要在本地调用真实服务，应设置 `AI_ENABLE_REAL_CALLS=True`；
该开关为 `False` 时只会生成 mock 文件。
```

## 后台管理

进入 Django Admin 的「AI 集成」菜单：

- **模型配置**：维护不同服务商、模型 ID、API Key 和超时等参数。
  - 同一服务商下配置名称唯一。
  - 可将常用配置设为默认。
  - API Key 在表单中以密码输入框展示，避免泄露。
- **生成任务**：选择模型配置、任务类型、填写提示词并上传参考图片后保存。
  - 保存仅创建任务记录，不会立即调用 AI 服务。
  - 在生成任务列表页，每条记录显示「生成」操作按钮；点击后才投递 Celery 异步任务。
  - 任务成功后会自动将结果保存到默认文件存储，并显示「下载」按钮。
  - 旧任务若已有结果 URL 但尚未落盘，也会显示「下载」按钮；点击时会补充下载并保存。
  - 列表中以颜色区分状态：灰色待生成、蓝色生成中、绿色成功、红色失败、橙色已取消。
  - 列表额外展示提示词摘要、创建人、创建/开始/完成时间等字段。
  - 对失败或待生成任务可使用「重新执行所选任务」批量重试。

## 启动 Worker

生成任务依赖 Celery Worker 消费队列：

```bash
# 本地
uv run celery -A celery_app worker --loglevel=INFO

# Docker Compose
docker compose -f deploy/docker-compose.yml up -d worker
```

## 状态说明

| 状态 | 颜色 | 说明 |
|------|------|------|
| 待生成 | 灰 | 已创建本地记录，等待 Worker 执行。 |
| 生成中 | 蓝 | Worker 已向第三方创建任务并轮询状态。 |
| 成功 | 绿 | 第三方返回结果 URL，结果文件已尝试下载到本地。 |
| 失败 | 红 | 创建或轮询过程出错，错误信息已记录。 |
| 已取消 | 橙 | 第三方任务被取消。 |

## 扩展更多能力

当前默认实现视频生成。新增任务类型或服务商时：

1. 在 `apps/ai_integration/models.py` 的对应 `choices` 中增加选项。
1. 在 `apps/ai_integration/services.py` 中为新的 provider 或 task_type 实现创建与轮询逻辑。
1. 更新 `apps/ai_integration/forms.py` 放开表单校验限制。
1. 补充迁移、测试和 `db/ai_integration.sql`。

详细 Agent 开发约定见 `agent-docs/ai-integration.md`。
