# 第三十七批：Agent Skill 同步

本批以 `agent-docs/` 为唯一规范源，重新同步 `skill/references/`，并将模板技能统一升级为
`djangoharness-business`。

主要变更：

- Skill 新增架构设计路由，覆盖跨 App 依赖、状态机、事务、幂等、性能和大文件拆分。
- 完成门禁与最新 Agent 文档对齐，纳入文档构建、迁移漂移和 Skill 同步校验。
- 补齐通知、AI、博客等已有规范的生成产物，并修正技能界面元数据。
- 新增 Cookiecutter 测试，校验导航中的规范与 Skill references 内容完全一致、路由完整。

验证结果：

- `uv run pytest template_tests/test_cookiecutter_template.py -q`：通过，8 项测试成功。
- `python3 .../skill-creator/scripts/quick_validate.py {{cookiecutter.project_slug}}/skill`：通过。
- `diff -rq --exclude 'async-tasks copy.md' agent-docs skill/references`：通过，导航规范与
  Skill references 无内容漂移；未同步误生成的 `async-tasks copy.md`。
- `git diff --check`：通过。

本批只修改 Cookiecutter 的 Skill 与模板测试，未改变生成项目的 Django 代码、依赖或模型，
因此未重复执行生成项目的完整 Django、文档与迁移门禁。
