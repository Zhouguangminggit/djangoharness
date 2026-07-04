# 第二十一批：allauth 注册验证

## 变更

- 账号和手机注册均接入 allauth SignupView 生命周期。
- 账号注册创建 EmailAddress；手机注册设置 `phone_verified=True` 且排除占位邮箱。
- Adapter 对接现有验证码缓存、Celery 和 Provider，开发环境继续使用固定验证码。
- 欢迎邮件仅在第三方服务开启时异步调度。

## 验证

- 账号注册、手机注册、重复身份、验证码发送、消费和异步 Provider 测试通过。
