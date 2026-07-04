# 第二十批：allauth 登录退出

## 变更

- 登录与退出改用 allauth 视图生命周期。
- 登录表单支持用户名、邮箱、手机号和历史 POST 字段。
- 保留 `accounts:*`，并提供 `account_login`、`account_logout`。
- 安全跳转只接受当前 Host，退出只接受 POST。

## 验证

- 三种登录标识、停用用户、保持登录、外部 next 拒绝和 POST 退出测试通过。
- 图片/视频认证页沿用现有模板和媒体配置。
