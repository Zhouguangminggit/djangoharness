# 第二十批：allauth 登录退出

## 变更

- 登录与退出改用 allauth 视图生命周期。
- 登录表单支持用户名、邮箱、手机号和历史 POST 字段。
- 保留 `accounts:*`，并提供 `account_login`、`account_logout`。
- 安全跳转只接受当前 Host，退出只接受 POST。

## 验证

- 三种登录标识、停用用户、保持登录、外部 next 拒绝和 POST 退出测试通过。
- 图片/视频认证页沿用现有模板和媒体配置。

## 修复记录

- 登录表单统一将输入交给 `MultiIdentifierBackend`，不再依赖 allauth 对用户名、邮箱和
  手机号格式的预判。
- 新增三种标识通过真实 allauth 登录视图建立会话的参数化回归测试。
- `make check`：59 项测试通过。
