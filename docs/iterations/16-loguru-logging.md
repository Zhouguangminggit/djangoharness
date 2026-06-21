# 第十六批：Loguru 日志集成

## 变更

- 增加 Loguru 运行依赖和统一日志配置模块。
- 将 Python 标准库、Django 和 Gunicorn 日志转发到 Loguru，并保留业务调用位置。
- 本地与生产终端支持 ANSI 分级颜色；可选文件 sink 支持轮转、保留和 gzip 压缩。
- 禁止 Celery 重置 root logger，使 Worker 内业务日志继续使用统一配置。
- 同步 `.env.example`、Agent 日志规范和 skill 路由。
- 增加颜色终端、无 ANSI 文件日志及标准库桥接测试。
- 将 Django 自动重载器单独限制为 `INFO`，避免开发终端被逐文件 mtime 扫描日志刷屏。
- 开发环境整体最低级别调整为 `INFO`，不再输出 DEBUG 日志。
- 本地默认将应用、异步和错误日志分别写入 `logs/app.log`、`logs/async.log`
  和 `logs/error.log`。
- 增加请求日志中间件，写入 request ID、用户 ID、脱敏用户名、认证状态、IP、方法、
  路径、状态码和耗时。

## 验证

- `make format`：通过。
- `make lint`：通过，包含 Ruff、mypy、Markdown 和 Django 系统检查。
- `UV_CACHE_DIR=.uv-cache uv lock --check`：通过，解析 50 个包。
- `UV_CACHE_DIR=.uv-cache uv run --no-sync pytest tests/test_logging.py -q`：通过，4 项日志测试
  全部通过。
- `make test`：未全部通过，37 项通过、1 项失败。失败项为既有
  `tests/test_accounts.py::test_home_page` 期待的首页文案与当前模板不一致，与本批日志
  变更无关。
- `make check`：未全部通过；静态检查通过，随后被同一首页文案测试阻塞。

## 遗留项

- 需由首页需求所属批次确认是恢复“把业务想法，落到可靠的工程底座上”文案，还是更新已过期的
  测试断言。
