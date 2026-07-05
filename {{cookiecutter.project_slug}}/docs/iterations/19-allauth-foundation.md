# 第十九批：allauth 基础与迁移

## 变更

- 通过 uv 锁定 `django-allauth>=65.18,<66`。
- 注册 account app、middleware、认证后端和官方 URL。
- 新增 `phone_verified`、Account Adapter 和 MySQL 8 参考字段。
- 数据迁移将存量手机号和真实邮箱标记为已验证，排除手机占位邮箱。

## 验证

- `uv run python manage.py check`：通过。
- `uv run pytest tests/test_accounts.py -q -k 'not home_page'`：28 通过。

## 回滚

先备份生产数据库，再回滚 `accounts.0004_allauth_identity_state`。反向迁移保留
EmailAddress，避免误删上线后新增关联；确认不再使用 allauth 后再单独回滚 account
migrations。
