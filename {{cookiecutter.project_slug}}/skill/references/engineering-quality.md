# 工程质量规范

## 依赖

- 依赖只在 `pyproject.toml` 声明，并提交更新后的 `uv.lock`。
- 运行依赖放 `project.dependencies`，开发工具放 `dependency-groups.dev`。
- 使用 `uv add` 或 `uv add --dev` 更新依赖；禁止恢复 `requirements.txt` 双源管理。

## 代码质量

- `make format` 自动修复 Ruff 问题并格式化 Python、Markdown。
- `make lint` 执行 Ruff、mypy、Markdown 和 Django 系统检查。
- `make test` 执行 pytest；`make check` 是提交前完整检查入口。
- 新增公共函数应提供类型标注。不要用全局忽略规避可修复的类型或静态检查问题。

## 测试

- 每项行为至少覆盖成功路径；输入校验、权限和异常处理应覆盖关键失败路径。
- 外部邮件、Redis、Celery broker 和第三方 API 必须 mock 或替换，测试不能依赖网络服务。
- 数据库测试使用 pytest-django；默认 SQLite，MySQL 专属行为需单独标记并说明执行方式。

## Git 与批次

- 每次提交只包含一个可说明的主题，不覆盖用户已有的无关修改。
- 每批完成后更新 `docs/iterations/`，记录命令的真实结果；失败项不能写成已完成。
- 合并前必须保证 `uv lock --check` 和 `make check` 成功。
