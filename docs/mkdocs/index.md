# 文档站概览

文档站使用 MkDocs 与 Material for MkDocs 构建，支持中文搜索、响应式导航、深浅色主题、
代码复制、提示块、内容标签和静态部署。

<div class="grid cards" markdown>

- :material-file-document-edit-outline: **编写与预览**

  在 `docs/` 中维护 Markdown，通过 `make docs-serve` 实时预览。

  [查看使用说明](guide.md)

- :material-cloud-upload-outline: **构建与部署**

  严格检查站内链接，并将生成的 `site/` 发布到静态托管服务。

  [查看部署说明](guide.md#deployment)

- :material-server-security: **生产配置**

  配置 Django、MySQL、Redis、媒体文件与发布检查。

  [查看生产配置](../deploy.md)

</div>
