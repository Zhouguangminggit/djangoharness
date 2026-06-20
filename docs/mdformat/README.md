# mdformat是什么

mdformat 是 Markdown 格式化工具。

## 有什么帮助

它让 README、工具文档和 Agent 规范保持一致格式，并由 CI 检查漂移。

## 如何使用

```bash
make format
uv run mdformat --check README.md README.en.md agent-docs docs
```

格式检查失败时运行 `make format`，再检查文档内容是否仍准确。
