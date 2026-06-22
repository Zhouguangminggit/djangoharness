# uv是什么

uv 是项目的 Python 版本、虚拟环境、依赖和锁文件工具。

官方文档：https://hellowac.github.io/uv-zh-cn/getting-started/features/

## 有什么帮助

`pyproject.toml` 声明依赖、支持的 Python 版本和默认包索引，`uv.lock` 固定跨 Python
版本及跨平台的解析结果，避免不同机器安装出不一致的版本。

## 如何使用

```bash
uv python install 3.10            # 安装 Python；也支持 3.11、3.12、3.13
uv python pin 3.10                # 写入 .python-version，选择工作区解释器
uv sync --all-groups --locked     # 严格按锁文件安装运行与开发依赖
uv add <package>                   # 新增运行依赖
uv add --dev <package>             # 新增开发依赖
uv lock --check                    # 确认锁文件未过期
uv run python manage.py runserver  # 在项目环境运行命令
```

项目支持 Python 3.10～3.13。切换解释器后重新执行同步，例如：

```bash
uv python pin 3.12
uv sync --all-groups --locked
```

## 包索引与故障排查

项目在 `pyproject.toml` 中将清华 PyPI 镜像配置为 uv 默认索引，锁文件中的包也来自该
镜像。不要仅使用 `--index-url` 临时同步旧锁文件，否则 uv 仍可能按锁文件中的
`files.pythonhosted.org` 地址下载。

若镜像暂时不可用，可以为单次命令改用官方 PyPI；由于索引发生变化，应允许 uv 更新
锁文件：

```bash
UV_DEFAULT_INDEX=https://pypi.org/simple uv lock
UV_DEFAULT_INDEX=https://pypi.org/simple uv sync --all-groups --locked
```

恢复清华镜像时执行 `uv lock`，再同步并提交更新后的 `uv.lock`。安装失败时依次检查：

1. `uv run python --version` 是否在 3.10～3.13 范围内。
2. `uv lock --check` 是否通过。
3. 报错 URL 是否来自 `pypi.tuna.tsinghua.edu.cn`。
4. macOS 安装 `mysqlclient` 失败时，是否已按 `docs/macos/README.md` 安装 MySQL
   客户端编译依赖。


## 常见问题

1. 安装依赖失败或者太慢时，检查网络连接，如果有开vpn，需要关闭vpn重试。
