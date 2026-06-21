# Admin 用户表单 Design QA

- source visual truth path: `docs/design/admin-form-full-width-target.png`
- implementation screenshot path: unavailable
- viewport: 1440 × 1024
- state: 用户编辑表单
- full-view comparison evidence: blocked；内置 Browser 与 Chrome 均因当前运行环境缺少浏览器沙箱元数据而无法连接。
- focused region comparison evidence: blocked；无法取得实现截图，未进行伪造或仅凭代码判断的视觉对比。

## Findings

- [P1] 缺少实现后视觉证据
  - Location: 用户新增和编辑表单。
  - Evidence: 选定设计稿可读取，但本地实现无法通过可用浏览器捕获。
  - Impact: 无法确认 1440 × 1024 下的真实宽度、字段对齐、SimpleUI 样式覆盖和权限选择器尺寸。
  - Fix: 获得 Playwright 使用授权，或由用户提供更新后的新增页和编辑页截图，再执行同视口对比。

## Open Questions

- 是否允许在首选 Browser 与 Chrome 均不可用时，使用 Playwright 捕获本地页面？

## Implementation Checklist

- 捕获 1440 × 1024 用户编辑页与新增页。
- 将实现截图与设计稿合并为同一比较输入。
- 修复全部 P0/P1/P2 差异并复测。

## Follow-up Polish

- 待截图后评估小屏断点和文件上传控件的浏览器原生差异。

## Patches Made

- 表单改为全宽单表面和分区式两列网格。
- 统一字段、帮助文本、只读值、文件上传、权限选择器和底部操作栏样式。
- 新增页补齐个人信息与权限分区。

final result: blocked
