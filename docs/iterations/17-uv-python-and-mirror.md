# 第十七批：uv Python 版本与国内镜像

## 变更

- 将项目支持范围明确为 Python 3.10～3.13，避免未验证的新 Python 大版本进入解析范围。
- 在 `pyproject.toml` 中将清华 PyPI 镜像设置为 uv 默认索引，并同步更新锁文件。
- 快速开始增加 Python 安装、固定版本、严格按锁文件同步和版本切换命令。
- uv 专题文档增加镜像切换、锁文件行为和安装故障排查说明。

## 验证

- `UV_CACHE_DIR=.uv-cache uv lock --check --offline`：通过，解析 50 个包，锁文件与
  `pyproject.toml` 一致。
- Python 3.10、3.11、3.13 分别执行 `uv sync --all-groups --locked --dry-run --offline --python <version>`：通过，均能从同一锁文件选择对应依赖。
- 锁文件包含 mypy 1.20.2 对 Python 3.10、3.11、3.12、3.13 的 macOS ARM64 wheel，
  下载域名均为 `pypi.tuna.tsinghua.edu.cn`。
- `git diff --check`：通过。
- Markdown 格式检查未执行：当前 `.venv` 因此前同步失败而不包含 `mdformat`，且当前
  执行环境访问清华、阿里云和腾讯云镜像均 DNS 超时，无法补装工具。

## 遗留项

- 当前机器未安装 Python 3.12，因此未执行该版本的同步 dry-run；锁文件已包含其平台
  wheel，需在装有 Python 3.12 的环境或 CI 中补充完整同步验证。
- 网络恢复后执行 `uv sync --all-groups --locked`，再运行 `make check` 完成全量验收。
