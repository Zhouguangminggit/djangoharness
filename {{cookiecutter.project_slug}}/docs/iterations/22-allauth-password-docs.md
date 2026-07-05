# 第二十二批：allauth 密码与文档

## 变更

- 启用 allauth 密码重置验证码流程和防枚举。
- 保留历史密码重置 URL，并开放官方 `account_reset_password*` 路由。
- 增加 allauth 页面覆盖模板、认证指南、Agent 规范和 MkDocs 导航。

## 验证

- allauth 固定邮箱验证码、设置新密码及完成后不可复用的主流程测试通过。
- `make format`：通过。
- `make lint`：通过。
- `make test`：40 项通过。
- `uv lock --check`：通过。
- `make check`：通过，包含 40 项测试。
- `makemigrations --check --dry-run`（使用临时 SQLite）：通过，无模型变更。
- 全新临时 SQLite 执行全部 migrations：通过。
