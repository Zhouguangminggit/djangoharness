# DjangoHarness Cookiecutter 模板

本仓库用于通过 Cookiecutter 生成人工可继续开发的 DjangoHarness 业务项目。无需提前
克隆仓库，可以直接指定 GitHub 仓库和模板分支生成最终业务项目。

Cookiecutter 模板仓库本身会包含 `{{cookiecutter.project_slug}}/`、`hooks/`、
`template_tests/` 等模板配置目录；这些目录只用于模板维护，不应该作为业务项目提交。
业务项目应只提交生成后的项目内容。

## 在当前空 Git 目录生成项目

如果已经新建了业务项目目录并执行了 `git init`，推荐先生成到临时目录，再把生成项目的
内容同步到当前目录。这样当前目录会直接变成最终 Django 项目，不会留下
`{{cookiecutter.project_slug}}/`、`hooks/`、`template_tests/` 等模板维护文件：

```bash
mkdir campus-second-platform
cd campus-second-platform
git init

tmpdir="$(mktemp -d)"
uv tool run cookiecutter \
  https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business \
  --output-dir "$tmpdir"

rsync -a "$tmpdir/<project_slug>/" ./
rm -rf "$tmpdir"
git status --short
```

执行 Cookiecutter 交互参数时，`project_slug` 填写的值需要与 `rsync` 命令中的
`<project_slug>` 一致。例如填写 `campus-second-platform`，则同步命令为：

```bash
rsync -a "$tmpdir/campus-second-platform/" ./
```

生成后从当前目录继续安装依赖、运行迁移和提交 Git 即可。

## 直接从 GitHub 分支生成

如果还没有创建业务项目目录，也可以在父目录直接生成一个新的项目目录。推荐使用 uv
临时运行 Cookiecutter，不会向当前项目安装额外依赖：

```bash
mkdir my-projects
cd my-projects

uv tool run cookiecutter \
  https://github.com/Zhouguangminggit/djangoharness.git \
  --checkout business
```

Cookiecutter 会自动克隆 `business` 分支、询问模板参数，并在当前目录生成以
`project_slug` 命名的业务项目目录。也可以通过 `--output-dir` 指定输出位置：

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

只有需要修改或调试模板时，才需要克隆本仓库。克隆后的目录是模板维护目录，不是最终
业务项目目录：

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
