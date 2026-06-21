# 第六批：自定义用户模型

## 完成内容

- 新增 `accounts.User`、用户管理器和多标识认证后端。
- 增加初始 migration 和 MySQL 8 参考 SQL。
- 重建示例 SQLite 数据库，并保留原 admin 的密码哈希和权限。

## 验证

- `uv run python manage.py migrate`：通过。
- 其余完成检查统一记录在第十批验收文档。
