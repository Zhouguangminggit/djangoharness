# 开发环境

选择操作系统后完成 Python、uv 和项目依赖配置。本地默认使用 SQLite；需要异步任务或生产
等价环境时，再启用 Redis、MySQL 和 Docker。

<div class="grid cards" markdown>

- :simple-apple: **macOS**

  使用 Homebrew 安装工具链，支持 Apple Silicon 与 Intel Mac。

  [打开 macOS 指南](../macos/README.md)

- :fontawesome-brands-windows: **Windows**

  使用 PowerShell、Git Bash 或 WSL 运行项目。

  [打开 Windows 指南](../windows/README.md)

</div>

!!! tip "端口约定"

```
Django 开发服务器默认使用 `8000`，MkDocs 文档服务器使用 `8001`，两者可同时运行。
```
