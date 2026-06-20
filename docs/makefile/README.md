# Makefile是什么

Makefile 是项目统一命令入口。

## 有什么帮助

开发者、本地 Agent 和 CI 使用同一组命令，不需要分别记忆工具参数。

## 如何使用

```bash
make sync    # 安装全部依赖
make format  # 自动修复和格式化
make lint    # 静态检查、类型检查和 Django 检查
make test    # 运行测试
make check   # lint + test
```

若提示找不到 `uv`，先执行 `python -m pip install uv`。
