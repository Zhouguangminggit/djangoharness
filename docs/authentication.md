# 用户认证

DjangoHarness 使用 `django-allauth>=65.18,<66` 管理本地账户的登录、注册、退出和
密码重置生命周期。当前不启用社交登录、MFA、无密码登录或 headless API。

## 入口与兼容性

官方路由和历史路由同时保留：

| 功能 | 官方路由名 | 兼容路由名 |
| --- | --- | --- |
| 登录 | `account_login` | `accounts:login` |
| 退出 | `account_logout` | `accounts:logout` |
| 注册 | `account_signup` | `accounts:register` |
| 密码重置 | `account_reset_password` | `accounts:password_reset` |

退出只接受 POST。用户名、邮箱和手机号均可用于密码登录。认证页面继续读取
`AUTH_STYLE` 和三个 `AUTH_*_MEDIA` 环境变量渲染图片或视频背景。

## 账号与验证

- 账号注册需要用户名、真实邮箱和两次密码，注册后直接登录。
- 手机注册需要中国大陆手机号、验证码和两次密码；系统生成内部用户名和占位邮箱。
- 真实邮箱由 allauth `EmailAddress` 维护。占位邮箱不会写入该表。
- 本地开发使用 `AUTH_FIXED_SMS_CODE` 和 `AUTH_FIXED_EMAIL_CODE`，不访问 Redis、
  Celery 或外部 Provider。
- 生产开启 `USE_THIRD_PARTY_SERVICES` 后，验证码写入 verification cache，经 Celery
  调用 Provider 发送，并执行有效期、冷却和尝试次数限制。

## 升级与回滚

部署前先备份数据库，再执行 `uv run python manage.py migrate`。迁移会新增
`phone_verified`，将已有手机号视为已验证，并为真实邮箱创建已验证的 primary
`EmailAddress`。密码散列、用户主键和现有会话不变。

回滚 `accounts.0004_allauth_identity_state` 会移除 `phone_verified` 字段，但有意保留
EmailAddress，避免误删上线后新增的邮箱关联。确认不再使用 allauth 后，才能单独回滚
allauth 的 account migrations。生产回滚前必须备份数据库。

实现依据为 allauth 官方
[Quickstart](https://docs.allauth.org/en/latest/installation/quickstart.html)、
[账户配置](https://docs.allauth.org/en/latest/account/configuration.html)和
[手机号扩展](https://docs.allauth.org/en/latest/account/phone.html)。
