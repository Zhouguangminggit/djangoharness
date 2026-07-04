# 消息通知

项目使用 `django-notifications-hq` 存储站内通知，并由
`apps.notifications_center` 提供稳定的业务接入、后台发布和前台通知中心。

## 安装与配置

依赖由 uv 统一管理。`notifications` 必须位于产生通知的业务应用之后。项目启用了
`DJANGO_NOTIFICATIONS_CONFIG["USE_JSONFIELD"]`，用于保存通知的站内跳转路径。首次部署
执行常规迁移即可创建第三方通知表和项目发布记录表：

```bash
uv run python manage.py migrate
```

## 后台发布

管理员进入“消息通知 → 发布通知”，填写标题、正文、级别和可选站内路径，然后选择：

- 全部启用用户：发布时向所有 `is_active=True` 的账号发送。
- 指定用户：至少选择一个启用账号。

保存即同步发布。成功发布后的记录只读，不能编辑、删除或重复发送。发布记录保存发布人、
发布时间和实际发送数量。大量用户广播可能增加后台请求耗时，达到实际性能瓶颈后应迁移到
具备幂等控制的 Celery 任务。

## 业务代码接入

业务模块只能调用适配服务，不直接调用第三方 `notify.send()`：

```python
from apps.notifications_center.services import send_notification

send_notification(
    actor=request.user,
    recipients=order.owner,
    title="订单状态已更新",
    body="订单已进入审核阶段。",
    level="info",
    target_path=f"/orders/{order.pk}/",
    action_object=order,
)
```

`recipients` 可以是单个用户或可迭代用户集合，服务会按主键去重。`level` 仅支持
`success`、`info`、`warning` 和 `error`。`target_path` 只能是以 `/` 开头且不以
`//` 开头的站内路径。空收件人集合不会创建通知。

## 前台通知中心

登录用户可以从页头“消息”入口查看通知：

- 按全部、未读或已读筛选，时间倒序展示，每页 20 条。
- 单条标为已读或未读，或者将全部未读消息标为已读。
- 只能查看和修改自己的通知。
- 业务链接不会隐式修改通知状态。

所有读状态修改均为带 CSRF 防护的 POST 请求。当前模块不包含删除、邮件、短信、推送、
定时发布、用户组、动态人群、定时轮询和 WebSocket。

## 数据边界

第三方 `notifications_notification` 表由第三方 migration 管理。项目自有的
`NotificationPublication` 仅记录后台发布配置和结果；其 migration 是执行源，
`db/notification_publication.sql` 是 MySQL 8 评审参考，不应代替 Django migration。
