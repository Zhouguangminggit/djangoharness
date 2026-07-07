# 29 Cookiecutter 当前目录落地说明

## 目标

修正模板使用说明，避免业务项目误提交模板维护目录，并提供在已初始化 Git 的空目录中
直接落地最终 Django 项目的操作路径。

## 变更

- 根 README 增加当前空 Git 目录生成流程：先生成到临时目录，再同步生成项目内容到当前目录。
- 模板内 `docs/cookiecutter/README.md` 同步区分模板维护目录与最终业务项目目录。
- 模板测试增加生成物边界断言，确认生成项目不包含 `hooks/`、`template_tests/`、
  `cookiecutter.json` 或未渲染的 `{{cookiecutter.project_slug}}/` 目录。

## 验证记录

- `uv run pytest template_tests -q`（模板仓库）：通过，7 个测试全部通过。
- `uv run cookiecutter . --no-input --output-dir <tmpdir>`（模板仓库）：通过，临时生成项目成功。
- `uv run mkdocs build --strict`（临时生成项目）：通过，MkDocs 严格模式构建成功；输出中仍包含
  Material for MkDocs 的上游提示和既有历史迭代页未加入 `nav` 的信息。

## 已知限制

- Cookiecutter 原生会创建以 `project_slug` 命名的顶层目录。已存在的当前目录不应通过
  覆盖模式直接生成，避免误删 `.git` 或已有文件。
