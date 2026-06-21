# Loguru 日志规范

本文与 [`agent-docs/logging.md`](../../agent-docs/logging.md) 保持同步。

- 新业务代码使用 `from loguru import logger`，标准库日志由 `InterceptHandler` 转发。
- 使用 `{}` 占位符或 `logger.bind()` 记录稳定业务上下文，异常边界使用
  `logger.exception()`。
- 不记录密码、验证码、Cookie、Authorization header、token、密钥或完整隐私数据。
- 不在业务模块添加 sink；统一通过环境变量配置级别、颜色、文件轮转、保留与压缩。
- Django 自动重载器默认使用 `INFO`，不应在常规开发中输出逐文件 mtime 扫描日志。
- 开发与生产默认最低级别均为 `INFO`；本地分别写入 `logs/app.log`、
  `logs/async.log` 和 `logs/error.log`。
- HTTP 请求日志应包含 request ID、用户 ID、脱敏用户名、认证状态、IP、方法、路径、
  响应状态和耗时，不得记录原始密码、验证码或 token。
- 生产默认关闭 `LOG_DIAGNOSE`；日志采集器不支持 ANSI 时关闭 `LOG_COLORIZE`。
