# uv是什么

uv 是项目的 Python 版本、虚拟环境、依赖和锁文件工具。

官方文档：https://hellowac.github.io/uv-zh-cn/getting-started/features/

## 有什么帮助

`pyproject.toml` 声明依赖，`uv.lock` 固定解析结果，避免不同机器安装出不同版本。

## 如何使用

```bash
uv sync --all-groups              # 安装运行与开发依赖
uv add <package>                   # 新增运行依赖
uv add --dev <package>             # 新增开发依赖
uv lock --check                    # 确认锁文件未过期
uv run python manage.py runserver  # 在项目环境运行命令
```

安装失败时先确认 Python 版本为 3.10+
