# 第十四批：个人中心密码与头像

## 完成内容

- 个人中心新增同页密码修改表单，校验旧密码后才允许设置新密码。
- 密码修改成功后刷新会话认证哈希，当前设备保持登录。
- 移除跳转忘记密码页面的修改密码链接。
- 用户模型增加头像字段，文件保存到 `media/avatars/<用户ID>/`。
- 限制头像为有效 JPG、PNG、WebP 且不超过 5MB，使用随机文件名。
- 替换头像及删除用户时清理旧媒体文件。
- 开发环境增加 `/media/` 访问路由，生产文档补充媒体持久化与反向代理要求。
- 增加 Pillow 运行依赖，并同步 migration、MySQL 参考 SQL 和锁文件。

## 验证结果

- 定向认证与个人中心测试：27 项通过。
- `make format`：通过。
- `make lint`：通过。
- `make test`：29 项通过。
- `uv lock --check`：通过，解析 48 个包。
- `make check`：通过，29 项测试通过。
- `uv run python manage.py makemigrations --check --dry-run`：通过，无变更。
