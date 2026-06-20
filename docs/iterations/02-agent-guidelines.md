# 第二批：Agent 规范

## 产出

- 建立 `agent-docs/AGENTS.md` 渐进式导航。
- 拆分项目结构、Django、工程质量、异步任务和数据库规范。
- 统一完成定义与批次记录要求。
- 修正 `db/user.sql`，并明确 migration 与参考 SQL 的边界。
- 旧 Trae 规则改为指向统一规范入口。

## 验证

导航链接和 Markdown 格式纳入 `make lint`。

## 遗留项

本轮不生成 Codex skill；未来应以该规范体系为输入生成。
