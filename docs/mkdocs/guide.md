# MkDocs + Material 使用与部署

项目使用 MkDocs 生成静态文档站，并使用 Material for MkDocs 提供响应式界面、全文搜索、
代码复制、深浅色主题和层级导航。

## 安装与启动

MkDocs Material 属于开发依赖，已由 `pyproject.toml` 和 `uv.lock` 锁定：

```bash
uv sync --all-groups --locked
make docs-serve
```

本地访问地址为 <http://127.0.0.1:8001/>。Django 开发服务器仍使用
<http://127.0.0.1:8000/>，两者可以同时运行。

如需让局域网设备访问，可直接执行：

```bash
uv run mkdocs serve --dev-addr 0.0.0.0:8001
```

此方式会监听所有网络接口，只应在可信网络中使用。

## 添加业务主题文档

1. 在 `docs/` 下建立清晰的业务目录，例如 `docs/orders/`。
1. 使用 `.md` 文件编写页面，例如 `docs/orders/index.md`。
1. 在 `mkdocs.yml` 的 `nav` 中添加页面，确保站点导航可发现。
1. 使用相对于当前文档的路径引用其他文档或图片。
1. 执行 `make docs-build`，修复全部警告后再提交。

示例导航：

```yaml
nav:
  - 订单业务:
      - 概览: orders/index.md
      - 接口说明: orders/api.md
```

## 常用 Markdown 能力

### 提示块

```markdown
!!! warning "上线前检查"
    必须使用生产配置构建和验收。
```

### 可折叠内容

```markdown
??? note "查看详细说明"
    这里放置补充内容。
```

### 代码高亮

````markdown
```python
def health_check() -> str:
    return "ok"
```
````

以上能力由 `mkdocs.yml` 中的 `admonition` 和 `pymdownx` 扩展提供。调整站点名称、主题颜色、
功能和导航时，应修改该配置文件。

## 构建与验收

```bash
make docs-build
```

该命令以严格模式生成 `site/`。链接、导航或配置警告会导致构建失败。`site/` 是可重新生成的
静态产物，已加入 `.gitignore`，不应提交。

## 部署静态站点 { #deployment }

### Nginx 或静态托管

先生成站点：

```bash
uv sync --all-groups --locked
make docs-build
```

将 `site/` 的全部内容发布到 Nginx、对象存储静态网站、CDN 或其他静态托管服务。Nginx
最小配置示例：

```nginx
server {
    listen 80;
    server_name docs.example.com;
    root /srv/djangoharness/site;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

生产环境建议启用 HTTPS，并在反向代理或 CDN 层配置缓存、访问日志和安全响应头。若部署路径
不是域名根路径，需将 `mkdocs.yml` 的 `site_url` 设置为最终公开地址后重新构建。

### GitHub Pages

仓库维护者可在具备 GitHub 推送权限的环境中执行：

```bash
uv run mkdocs gh-deploy --strict
```

该命令会构建站点并推送 `gh-pages` 分支，属于远程写操作。正式流水线中应使用最小权限的
GitHub Actions token，并在部署前先执行 `make docs-build`。
