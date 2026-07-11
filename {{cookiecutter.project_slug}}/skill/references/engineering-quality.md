# 工程质量规范

## 依赖

- 依赖只在 `pyproject.toml` 声明，并提交更新后的 `uv.lock`。
- 运行依赖放 `project.dependencies`，开发工具放 `dependency-groups.dev`。
- 使用 `uv add` 或 `uv add --dev` 更新依赖；禁止恢复 `requirements.txt` 双源管理。
- MkDocs、主题和文档扩展属于开发工具，必须放入 `dependency-groups.dev`。

## 代码质量

- `make format` 自动修复 Ruff 问题并格式化 Python、Markdown。
- `make lint` 执行 Ruff、mypy、Markdown 和 Django 系统检查。
- `make test` 执行 pytest；`make check` 是提交前完整检查入口。
- `make docs-serve` 在 `127.0.0.1:8001` 提供文档热更新服务；`make docs-build`
  使用严格模式构建文档。
- 新增公共函数应提供类型标注。不要用全局忽略规避可修复的类型或静态检查问题。
- Ruff、mypy 通过只代表静态基线，不代表架构质量。评审还必须检查文件/函数规模、跨 App
  依赖、事务边界、状态迁移、查询数量和异常语义。

## 测试

- 每项行为至少覆盖成功路径；输入校验、权限和异常处理应覆盖关键失败路径。
- 外部邮件、Redis、Celery broker 和第三方 API 必须 mock 或替换，测试不能依赖网络服务。
- 数据库测试使用 pytest-django；默认 SQLite，MySQL 专属行为需单独标记并说明执行方式。
- 标准测试套件必须可在存在开发者 `.env` 时仍使用隔离的临时数据库，不连接开发、测试或生产 MySQL。
- 每个核心用例至少覆盖：成功、无权、非法状态、重复请求/幂等和交易回滚；涉及并发时补充针对目标数据库的集成测试。
- 列表、仪表盘和 context processor 的关键路径应增加查询数断言，防止 N+1 和聚合查询无界增长。

## Git 与批次

- 每次提交只包含一个可说明的主题，不覆盖用户已有的无关修改。
- 每批完成后更新 `docs/iterations/`，记录命令的真实结果；失败项不能写成已完成。
- 合并前必须保证 `uv lock --check` 和 `make check` 成功。
- 修改 `docs/` 或 `mkdocs.yml` 时必须同时运行 `make docs-build`；新增用户或业务页面必须加入
  `mkdocs.yml` 导航。不要提交生成的 `site/`。

## Skill 产物验证

- `agent-docs/` 中每个被导航的主题都必须在 `skill/references/` 有对应产物，并被
  `skill/SKILL.md` 的任务路由引用。
- 生成过程必须失败于断链、缺失引用、未解析占位符或源文档与产物内容漂移。
- 修改 Agent 规范后，至少执行 Markdown 格式检查、Skill 完整性检查和一个代表性生成/验收场景。
