# 开发工具

DjangoHarness 将依赖管理、格式化、静态检查和测试命令固化到项目配置中，确保本地开发与
持续集成执行相同规则。

| 工具 | 作用 | 文档 |
| --- | --- | --- |
| uv | Python、虚拟环境、依赖和锁文件 | [uv](../uv/README.md) |
| Makefile | 统一开发与验收命令 | [Makefile](../makefile/README.md) |
| Ruff | Python 格式化与代码检查 | [Ruff](../ruff/README.md) |
| mypy | 静态类型检查 | [mypy](../mypy/README.md) |
| pytest | 自动化测试 | [pytest](../pytest/README.md) |
| mdformat | Markdown 格式化 | [mdformat](../mdformat/README.md) |

## 常用验收命令

```bash
make format
make lint
make test
make docs-build
```
