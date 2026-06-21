# Loguru 日志规范

## 统一入口

- 新业务代码使用 `from loguru import logger`；Django、Gunicorn、Celery 和旧的
  `logging.getLogger()` 记录会经 `InterceptHandler` 统一转发。
- 禁止使用 `print()` 代替运行日志，禁止在业务模块重复添加 Loguru sink。
- 业务参数使用 Loguru 的 `{}` 占位符，例如
  `logger.info("验证码任务已调度 user_id={} purpose={}", user_id, purpose)`。
- 需要稳定检索字段时使用 `logger.bind(user_id=user_id, task_id=task_id)`，不要把
  整个 ORM 对象或 request 写入日志。

## 级别与异常

- `DEBUG`：仅用于开发诊断；`INFO`：关键业务状态；`WARNING`：可恢复异常或降级；
  `ERROR`：当前操作失败；`CRITICAL`：服务不可用或数据安全风险。
- 异常边界使用 `logger.exception("发送失败 user_id={}", user_id)` 保留堆栈，不要只记录
  `str(exc)`。
- 不记录密码、验证码、Cookie、Authorization header、token、密钥或完整个人隐私数据。

## 运行配置

- `LOG_LEVEL`：最低级别，开发和生产均默认 `INFO`，不在常规运行中输出 `DEBUG`。
- `DJANGO_AUTORELOAD_LOG_LEVEL`：Django 开发自动重载器级别，默认 `INFO`，避免输出每个
  Python 文件的 mtime 扫描记录；仅排查重载器时临时设为 `DEBUG`。
- `LOG_COLORIZE`：终端 ANSI 分级颜色，开发和生产默认开启；日志采集器不支持 ANSI
  时设为 `False`。
- 本地默认开启文件 sink：`LOG_FILE_PATH` 写应用与请求日志，
  `LOG_ASYNC_FILE_PATH` 写 Celery 和 `*.tasks` 日志，`LOG_ERROR_FILE_PATH` 写所有
  `ERROR` 及以上日志。默认对应 `logs/app.log`、`logs/async.log`、
  `logs/error.log`。
- `LOG_FILE_ENABLED=False` 可关闭全部文件 sink。容器开启文件日志时必须挂载
  `logs/` 持久化目录。
- `LOG_ROTATION`、`LOG_RETENTION`、`LOG_COMPRESSION`：控制单文件大小、保留时长和压缩方式。
- `LOG_BACKTRACE`、`LOG_DIAGNOSE`：扩展异常诊断；生产保持 `False`，避免泄露局部变量。

终端 sink 包含时间、级别、模块、函数和行号；文件 sink 额外包含进程和线程，且不写入
ANSI 控制字符，便于 `rg` 或日志平台检索。

## 请求上下文

`RequestLoggingMiddleware` 为每个请求绑定 `request_id`、`user_id`、脱敏
`username`、`is_authenticated`、`client_ip`、`method` 和 `path`，并记录状态码与耗时。
客户端 `X-Request-ID` 只有在符合安全格式时才会复用，否则由服务端生成；响应头会
返回最终 request ID。
