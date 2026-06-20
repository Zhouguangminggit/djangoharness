<p align="center">
  <img src="assets/djangoharness.png" alt="DjangoHarness" width="100%">
</p>

<p align="center"><strong>让 AI 按统一规范交付 Django 业务代码</strong></p>

<p align="center">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB">
  <img alt="Django 4.2" src="https://img.shields.io/badge/Django-4.2-0C4B33">
  <img alt="Celery 5" src="https://img.shields.io/badge/Celery-5-37814A">
  <img alt="Redis 6+" src="https://img.shields.io/badge/Redis-6%2B-DC382D">
  <img alt="MySQL 8" src="https://img.shields.io/badge/MySQL-8-4479A1">
  <img alt="uv" src="https://img.shields.io/badge/deps-uv-DE5FE9">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED">
  <img alt="Quality CI" src="https://img.shields.io/badge/CI-quality_passed-2088FF">
  <img alt="macOS" src="https://img.shields.io/badge/macOS-supported-000000">
  <img alt="Windows" src="https://img.shields.io/badge/Windows-supported-0078D4">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-blue">
</p>

中文 | [English](README.en.md)

# DjangoHarness

DjangoHarness 是面向 AI 编程初学者的 Django 前后端不分离脚手架。能够基于该框架和对应skill 让 Codex、claudecode等工具按快速、可检查、可测试的方式扩展业务。

## 为什么使用

- 目前自带登录、注册、密码重置、Django Admin 和模板基础结构。
- 用 uv、Ruff、mypy、pytest 和 mdformat 建立统一开发入口。
- 提供 Celery + Redis 异步任务骨架，本地测试无需启动 Redis。
- 使用渐进式 Agent 文档，减少重复提示和实现偏差，减少上下文信息。
- 同时保留 Django migration 与 MySQL 8 SQL 审查规范。

## 快速开始

环境要求：Python 3.10+、uv。生产使用 MySQL 8.x 和 Redis 6+；本地默认使用 SQLite数据库

```bash
# 未安装 uv 时
python -m pip install uv

# 安装锁定依赖
uv sync --all-groups

# 准备配置与数据库
cp .env.example .env
uv run python manage.py migrate

# 启动开发服务
uv run python manage.py runserver
```

访问主页 <http://127.0.0.1:8000/>

后台地址为 <http://127.0.0.1:8000/admin/>。

## 在 Codex 或 Claude Code 中使用项目 Skill

仓库中的 [`skill/`](skill/) 是由 DjangoHarness Agent 规范整理而成的完整项目 Skill。需要让 Codex 或 Claude Code 按本项目规范开发时：

1. 下载或克隆本仓库。
1. 将完整的 `skill/` 目录上传到 Codex 或 Claude Code 对应的项目、会话或 Skill 导入位置。
1. 保持目录结构不变，必须同时包含 `SKILL.md`、`references/`、`agents/` 和 `assets/`，不要只上传 `SKILL.md`。
1. 在任务中明确要求 AI 加载 DjangoHarness Skill，再开始编写或修改业务代码。

Skill 会向 AI 提供项目结构、Django 开发、异步任务、数据库和工程质量规范。不同工具版本的 Skill 导入入口可能不同，请以对应客户端当前界面为准。

## 开发命令

```bash
make format  # 自动修复并格式化 Python、Markdown
make lint    # Ruff、mypy、mdformat、Django system check
make test    # pytest
make check   # lint + test
```

## 文档导航

- [Agent 开发规范](agent-docs/AGENTS.md)
- [系统启用](docs/%E7%B3%BB%E7%BB%9F%E5%90%AF%E7%94%A8%E8%AF%B4%E6%98%8E.md)
- [macOS 使用说明](docs/macos/README.md)
- [Windows 使用说明](docs/windows/README.md)
- [Celery 使用](docs/celery/README.md)
- [Docker 部署](deploy/README.md)
- [工具文档](docs/makefile/README.md)
- [生产配置](docs/%E4%B8%8A%E7%BA%BF%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E.md)

## 贡献

Fork 仓库并从最新主分支创建主题分支。修改前阅读 Agent 规范；提交前运行 `make check`，模型变更同时提交 migration 和 `db/*.sql`，并在 Pull Request 中说明行为变化和验证结果。

## 联系作者与交流群

如果遇到项目使用、环境配置、工具安装或部署问题，请扫码添加作者微信。也可以扫码加入技术交流群，与其他技术爱好者交流 DjangoHarness 的使用经验和问题。

<table align="center">
  <tr>
    <th>作者微信</th>
    <th>技术交流群</th>
  </tr>
  <tr>
    <td align="center"><img src="assets/author.jpg" alt="作者微信二维码" width="280"></td>
    <td align="center"><img src="assets/group.jpg" alt="技术交流群二维码" width="280"></td>
  </tr>
</table>

## License

本项目使用 [MIT License](LICENSE)。
