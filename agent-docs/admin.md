# Django Admin 开发规则

## 配置边界

- SimpleUI 的品牌、菜单、首页和交互开关统一写在
  `base_framework/settings/admin.py`，业务后台注册写在对应 app 的 `admin.py`。
- 禁止在后台配置中写死外部业务地址、密钥或环境相关域名。
- 自定义菜单必须使用稳定的 Admin URL，并保持模块名称与 app 的 `verbose_name`
  一致。菜单项本身不提供权限隔离，后端视图仍必须检查 Django Admin 权限。

## 页面与数据

- 后台首页模板使用 `templates/admin/dashboard.html`，数据聚合放在 Python
  层，模板只负责展示；图表数据必须通过 `json_script` 安全传给 JavaScript。
- Admin 专属静态资源放在 `static/admin/css/` 和 `static/admin/js/`，禁止在模板中堆积大段样式或业务脚本。
- 列表页应提供必要的搜索、筛选、排序和分页；新增自定义入口时使用
  `ModelAdmin.get_urls()` 和 `admin_site.admin_view()`，不得绕过登录、CSRF 和权限校验。

## 用户管理

- 用户新增、修改和删除沿用 Django `UserAdmin` 的权限与密码哈希流程，禁止直接保存明文密码。
- 批量新增必须先校验完整文件，再在单个事务中写入；任一行失败时整批不落库。
- 批量文件限制体积和行数，并校验用户名、邮箱、手机号的库内及文件内重复。
- 批量启停不得停用当前登录账号；删除继续使用 Django Admin 原生确认页。

## 验证要求

- Admin 变更至少测试：首页访问权限与统计数据、用户增删改入口、批量导入成功、重复数据回滚和无权限访问。
- 完成后执行 `make format`、`make lint`、`make test`、`uv lock --check` 和
  `make check`，并在 `docs/iterations/` 记录真实结果。
