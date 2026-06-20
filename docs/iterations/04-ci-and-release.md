# 第四批：CI 与收口

## 产出

- 增加 push、pull request、手动触发的 GitHub Actions 质量检查。
- CI 使用 uv 锁定依赖并执行 `make lint`、`make test`。
- 第一阶段保留了原生产部署 workflow；其容器与健康检查缺口已在[第五批](05-platform-and-deployment.md)补齐。

## 最终验证

2026-06-20 本地验收结果：

- `uv lock --check`：通过，共解析 46 个包。
- `make format`：通过，无格式漂移。
- `make lint`：通过；Ruff、mypy、mdformat 和 Django system check 均无问题。
- `make test`：通过，共 4 个测试。

## 后续入口

未来生成 DjangoHarness Codex skill 时，以 `agent-docs/AGENTS.md` 及其链接规范为输入，不复制过时规则。
