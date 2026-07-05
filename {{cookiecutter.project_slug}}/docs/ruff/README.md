# Ruff是什么

Ruff 是 Python 代码检查和格式化工具。

## 有什么帮助

它统一导入顺序和代码格式，并提前发现未使用变量、错误写法及常见 Django 问题。

## 如何使用

通常运行 `make format` 和 `make lint`。需要单独定位问题时：

```bash
uv run ruff check apps tests
uv run ruff format --check apps tests
```

优先修复问题；只有确认规则不适用于特定代码时才添加范围最小的忽略。
