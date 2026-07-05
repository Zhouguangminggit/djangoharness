# Cookiecutter 模板使用说明

本项目由 DjangoHarness Cookiecutter 模板生成。Cookiecutter 只在创建项目时运行，
不属于 Django 运行时依赖。

## 生成项目

无需预先克隆模板仓库，可以直接从 GitHub 的 `business` 分支生成：

```bash
mkdir my-projects
cd my-projects
uv tool run cookiecutter \
  https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business
```

Cookiecutter 会自动获取指定分支，并在当前目录创建以 `project_slug` 命名的项目。
如需指定生成位置，可以增加 `--output-dir ~/Projects`。

本机已经安装 Cookiecutter 时，也可以直接执行：

```bash
cookiecutter https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business
```

需要修改或调试模板时，可以先克隆仓库，再从本地目录生成：

```bash
git clone --branch business \
  https://github.com/Zhouguangminggit/djangoharness.git
cd djangoharness
uv tool run cookiecutter .
```

生成过程需要填写：

| 参数 | 用途 | 示例 |
| --- | --- | --- |
| `product_name` | 页面、后台和文档使用的展示名称 | 校园二手交易平台 |
| `project_slug` | 英文技术短名 | campus-second-platform |
| `product_subtitle` | 首页和文档副标题 | 校园好物，就来校园二手交易平台 |
| `author_name` | License 和项目元数据中的作者 | 示例作者名 |

`project_slug` 必须以小写英文字母开头，只能包含小写英文字母、数字和连字符。
模板会自动派生 Python 包名、Docker 镜像变量、Compose 项目名和默认数据库名。

## 初始化生成项目

```bash
cd campus-second-platform
uv python install 3.10
uv python pin 3.10
uv sync --all-groups --locked
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py check
uv run python manage.py runserver
```

生产环境启动前还应配置 `.env` 中的密钥、域名、数据库、Redis 和邮件参数。

## 替换占位资源

模板不会自动生成产品图片。发布前应替换以下资源，并保持文件路径不变：

- `assets/product-banner.png`：README 产品横幅。
- `assets/logo.png`：项目通用 Logo。
- `static/accounts/brand/logo.png`：认证页和后台 Logo。
- `assets/author.jpg`、`assets/group.jpg`：作者及交流群占位图片。
- `static/core/img/poster.png`：首页产品展示图。

## 验证

```bash
uv lock --check
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
make lint
make test
make docs-build
docker compose -f deploy/docker-compose.yml config
```

重新生成项目会创建新目录，不会安全合并已有业务修改。已有项目应通过 Git 对比后人工迁移
模板更新。
