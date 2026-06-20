# 第五批：跨平台与容器部署

## 产出

- README 技术标签扩充至 Python、Django、Celery、Redis、MySQL、uv、Docker、CI、macOS、Windows 和 MIT。
- 增加 macOS、Windows 使用说明及 Celery 常用命令。
- 增加生产 Dockerfile、Compose 服务和 Dockerfile 专属忽略文件。
- 增加数据库健康检查端点，并纳入容器健康状态。
- 完善质量与生产部署 workflow，移除删除数据卷的发布步骤。

## 验证

2026-06-20 本地验收结果：

- `uv lock --check`：通过，共解析 47 个包。
- `make check`：通过；Ruff、mypy、mdformat、Django check 和 5 个测试均成功。
- migration 漂移检查：通过，无未生成变更。
- `docker compose config --quiet`：通过。
- 生产镜像构建：通过，Gunicorn、mysqlclient 与静态资源均进入最终镜像。
- 非 root 镜像冒烟测试：Docker 健康状态为 `healthy`，`/health/` 返回 200。
