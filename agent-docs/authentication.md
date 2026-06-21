# 用户认证规范

## 用户模型

- 始终使用 `get_user_model()` 或 `settings.AUTH_USER_MODEL`，禁止直接导入 Django 内置 `User`。
- 用户名、邮箱和手机号均可用于密码登录；新增账号必须保证邮箱唯一，手机号有值时唯一。
- 页面展示用户身份时统一使用 `user.display_name`，禁止直接展示手机号注册生成的内部随机用户名。展示顺序为昵称、脱敏手机号、用户名。
- 个人中心允许修改昵称、用户名和邮箱；手机号属于已验证登录标识，未实现验证码换绑前必须只读。
- 个人中心修改密码必须校验旧密码，成功后调用 `update_session_auth_hash()` 保持当前会话；不得跳转复用忘记密码流程。
- 用户头像保存到 `MEDIA_ROOT/avatars/<用户ID>/`，限制为有效的 JPG、PNG、WebP 且不超过 5MB；替换头像或删除用户时清理旧文件。
- 认证规则放在 `apps/accounts/` 的表单、服务或认证后端中，视图只负责编排请求和会话。

## 访问控制

- 主页、登录、注册、验证码发送、密码重置和健康检查为公开页面。
- 其他业务页面默认使用 `login_required`；类视图使用 `LoginRequiredMixin`，并将其放在继承列表首位。
- 修改数据的接口必须使用 POST 和 CSRF。仅在明确记录业务原因时才允许新增匿名访问页面。

## 验证码与外部服务

- 验证码用途必须使用 `VerificationPurpose`，按用途和接收方隔离缓存键。
- 生产验证码存入 Redis，并执行有效期、冷却、尝试次数和成功即消费规则。
- Celery 任务只负责发送边界，Provider 负责第三方协议；不得在日志中记录验证码、密码或密钥。
- 新 Provider 实现 `VerificationProvider`，通过配置注入地址和凭据，并使用 mock 编写测试。
- 固定验证码只用于本地或明确关闭第三方服务的受控环境；此模式不得访问验证码 cache、Redis、Celery 验证码任务或第三方 Provider。
- `dev.py` 必须将 `CACHES["verification"]` 固定为 `LocMemCache`。只有生产配置开启第三方服务时才允许切换到 Redis。
