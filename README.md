# DjangoHarness Cookiecutter 模板

本仓库用于通过 Cookiecutter 生成人工可继续开发的 DjangoHarness 业务项目。无需提前
克隆仓库，可以直接指定 GitHub 仓库和模板分支，将生成结果写入当前目录。

## 直接从 GitHub 分支生成

推荐使用 uv 临时运行 Cookiecutter，不会向当前项目安装额外依赖：

```bash
mkdir my-projects
cd my-projects

uv tool run cookiecutter \
  https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business
```

Cookiecutter 会自动克隆 `business` 分支、询问模板参数，并在当前目录生成以
`project_slug` 命名的项目目录。也可以通过 `--output-dir` 指定输出位置：

```bash
uv tool run cookiecutter \
  https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business \
  --output-dir ~/Projects
```

如果本机已经安装 Cookiecutter，可以使用等价命令：

```bash
cookiecutter https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business
```

## 从本地模板生成

克隆模板仓库并切换到模板分支后执行：

```bash
git clone --branch business \
  https://github.com/Zhouguangminggit/djangoharness.git
cd djangoharness
uv tool run cookiecutter .
```

生成时输入产品展示名称、英文短名、产品副标题和作者姓名。英文短名用于派生
Python 包名、Docker Compose 项目名、镜像变量和默认数据库名。

## 初始化生成项目

生成完成后进入项目目录并执行：

```bash
cd <project_slug>
uv sync --all-groups --locked
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py check
make test
```

完整的参数、资源替换和验收说明见模板内的
`docs/cookiecutter/README.md`。
