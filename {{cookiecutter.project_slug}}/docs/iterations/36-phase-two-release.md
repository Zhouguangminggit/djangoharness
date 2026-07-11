# 第三十六批：二期验收收口

验收使用 Cookiecutter 生成的 `phase-two-platform` 临时项目，结果如下：

- `make format`：通过，机械修正已同步回模板。
- `make lint`：通过，Ruff、格式、mypy、Markdown 与 Django check 均成功。
- `make test`：通过，102 项测试全部成功；第三方 notifications 包产生 23 条弃用警告。
- `make docs-build`：严格模式构建成功；既有未加入导航的历史迭代页仍由 MkDocs 提示。
- `uv lock --check`：通过，共解析 96 个包。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无迁移变化。
- `make check`：通过，102 项测试再次成功。
- `docker compose -f deploy/docker-compose.yml config --quiet`：通过。
- `uv run pytest template_tests/test_cookiecutter_template.py -q`：通过，7 项模板生成测试成功。

模板仓库级 Cookiecutter 测试同步修正了已过期的部署工作流断言。
