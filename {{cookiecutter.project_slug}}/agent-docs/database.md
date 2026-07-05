# 数据库与 SQL 规范

## 迁移是执行源

Django migration 是数据库结构的唯一执行源。`db/*.sql` 是供评审、DBA 和非 Django 部署场景使用的 MySQL 8 参考定义，不能替代 migration。

## 同步要求

- 新增或修改业务模型时运行 `uv run python manage.py makemigrations`。
- 每个业务模型在 `db/` 中维护对应 SQL，文件名使用小写蛇形命名。
- SQL 的表名、字段类型、默认值、非空、唯一约束和索引必须与 migration 一致。
- SQL 使用 InnoDB、`utf8mb4` 和可重复执行的 `CREATE TABLE IF NOT EXISTS`。
- Django 内置表通常由 migration 管理；若保留参考 SQL，必须注明不应手工重复创建。

## 验证清单

1. 执行 `uv run python manage.py makemigrations --check --dry-run`。
1. 检查 migration 在空数据库可应用，并有可行的回滚路径。
1. 对照 migration 审查 `db/*.sql` 的字段、约束和索引。
1. 运行涉及模型的单元测试以及 `make check`。
