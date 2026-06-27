# DjangoHarness 文档

<div class="hero" markdown>
<video width="100%" controls>   <source src="assets/video/video.mov" type="video/mp4">   您的浏览器不支持视频播放。 </video>

面向 AI 和 Agent 的 Django 业务开发框架，统一项目结构、工程质量、认证、异步任务、
后台管理和部署约定。

[快速开始](#local-start){ .md-button .md-button--primary }
[查看源码](https://github.com/Zhouguangminggit/djangoharness){ .md-button }

</div>

DjangoHarness 是面向 AI 和 Agent 的 Django 业务开发框架。本站集中展示框架能力、开发工具、
环境配置和部署说明，也可承载后续业务主题的 Markdown 文档。

## 文档入口

<div class="grid cards" markdown>

- :material-laptop:{ .lg .middle } **开发环境**

  ______________________________________________________________________

  在 macOS 或 Windows 上安装依赖并启动项目。

  [:octicons-arrow-right-24: 选择环境](environments/index.md)

- :material-tools:{ .lg .middle } **开发工具**

  ______________________________________________________________________

  使用 uv、Makefile、Ruff、mypy 和 pytest 保持交付一致。

  [:octicons-arrow-right-24: 查看工具](tools/index.md)

- :material-cube-outline:{ .lg .middle } **框架能力**

  ______________________________________________________________________

  配置 Celery、SimpleUI 和 DjangoHarness 内置能力。

  [:octicons-arrow-right-24: 浏览能力](framework/index.md)

- :material-book-open-page-variant:{ .lg .middle } **编写文档**

  ______________________________________________________________________

  使用 Material 组件编写和部署业务主题文档。

  [:octicons-arrow-right-24: 文档指南](mkdocs/guide.md)

</div>

## 本地启动 { #local-start }

完成项目依赖安装后，在仓库根目录运行：

```bash
make docs-serve
```

访问 <http://127.0.0.1:8001/>。文档服务固定使用 `8001`，不会与默认运行在 `8000`
端口的 Django 开发服务器冲突。

## 编写业务文档

在 `docs/` 下按业务主题创建目录和 Markdown 文件，然后将页面加入仓库根目录
`mkdocs.yml` 的 `nav`。提交前运行：

```bash
make docs-build
make check
```

详细配置、写作功能和部署方式见 [MkDocs + Material 使用说明](mkdocs/guide.md)。
