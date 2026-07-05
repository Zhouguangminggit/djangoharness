# pytest是什么

pytest 是测试运行器，pytest-django 提供 Django 数据库和客户端集成。

## 有什么帮助

测试验证页面、认证和任务行为，默认使用本地 SQLite数据库

## 如何使用

```bash
make test
uv run pytest tests/test_accounts.py
uv run pytest -k register
```

外部服务应 mock。出现数据库访问限制时，为测试添加 pytest-django 的数据库标记或 fixture。
