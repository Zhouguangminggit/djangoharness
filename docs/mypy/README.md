# mypy是什么

mypy 是 Python 静态类型检查工具，本项目同时启用 django-stubs。

## 有什么帮助

它在运行前发现参数、返回值和 Django 对象使用不一致的问题。

## 如何使用

```bash
make lint
uv run mypy apps base_framework celery_app tests manage.py
```

新增公共函数应补充类型标注。不要用全局 `ignore` 隐藏可修复问题。
