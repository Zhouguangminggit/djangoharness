/** DjangoHarness 产品介绍唯一运行时配置源。空链接或空图片不会渲染。 */
const CONFIG = {
  site: {
    name: "DjangoHarness",
    slogan: "让 AI 按工程标准交付 Django 产品",
    logo: "assets/logo.png",
    loginUrl: "/accounts/login/",
    docsUrl: "https://github.com/Zhouguangminggit/djangoharness"
  },
  navbar: { links: [
    { label: "框架能力", href: "#modules" },
    { label: "功能演示", href: "#video" },
    { label: "多端预览", href: "#design" },
    { label: "开始使用", href: "/accounts/login/" }
  ]},
  title: {
    badge: "AI-NATIVE DJANGO BUSINESS HARNESS",
    headline: "DjangoHarness",
    headlineAccent: "从业务需求到工程级交付",
    subline: "Django 4.2 · Cookiecutter · Agent 规范 · 自动化验收",
    desc: "面向不同业务主题的 AI 基座脚手架，让 Agent 在统一架构、质量、认证、后台、异步任务和部署规范下高效协作。"
  },
  design: {
    label: "标准化交付", title: "一套模板覆盖完整产品界面", subtitle: "前台、认证、后台与业务扩展使用一致的工程边界。",
    tabs: [
      { label: "Web 端", icon: "🖥️", image: "assets/design-web.png", desc: "Django 模板与分层静态资源构建响应式业务界面。" },
      { label: "业务应用", icon: "🧩", image: "assets/design-app.png", desc: "Accounts、Blog、Notifications 与 AI Integration 可直接扩展。" },
      { label: "管理后台", icon: "⚙️", image: "assets/design-admin.png", desc: "Unfold 提供统一仪表盘、筛选、操作和导入导出体验。" }
    ]
  },
  video: {
    leftTitle: { title: "DjangoHarness", subtitle: "工程规范即 Agent 上下文" },
    title: "快速了解标准化交付流程", brief: "从模板生成、依赖安装、开发测试到容器部署，完整展示可重复的工程链路。",
    videoSrc: "assets/demo.mp4", videoPoster: "assets/demo-poster.png",
    details: [
      { icon: "🧱", title: "工程基线", desc: "uv、Make、Ruff、mypy、pytest 与 MkDocs 统一门禁。" },
      { icon: "🤖", title: "Agent 规范", desc: "按任务渐进加载架构、认证、后台与业务开发规则。" },
      { icon: "🔐", title: "通用能力", desc: "认证、通知、Celery、日志和 AI Provider 开箱可用。" },
      { icon: "🚀", title: "部署验收", desc: "Cookiecutter、Docker Compose 与 CI 形成可重复交付。" }
    ]
  },
  modules: {
    label: "核心能力", title: "从工具集合升级为工程体系", subtitle: "每个模块都有代码、测试、文档和 Agent 规范。",
    items: [
      { icon: "👤", title: "认证体系", tag: "Accounts", desc: "allauth、验证码、资料、头像与权限控制。" },
      { icon: "🔔", title: "消息通知", tag: "Notifications", desc: "站内消息、后台发布与事务安全。" },
      { icon: "📝", title: "内容模块", tag: "Blog", desc: "分类、标签、作者、富文本与发布流程。" },
      { icon: "✨", title: "AI 集成", tag: "AI", desc: "Provider、Celery 任务、结果存储与后台操作。" },
      { icon: "🛠️", title: "工程质量", tag: "Quality", desc: "格式、类型、测试、文档与生成验收。" },
      { icon: "📦", title: "模板生成", tag: "Cookiecutter", desc: "按产品名称和项目标识生成独立业务工程。" }
    ]
  },
  footer: {
    slogan: "DjangoHarness — 让每次 AI 开发都可理解、可验证、可交付",
    license: "DjangoHarness · MIT License",
    author: { name: "__AUTHOR_NAME__", email: "" },
    links: [
      { label: "GitHub", href: "https://github.com/Zhouguangminggit/djangoharness" },
      { label: "小红书", href: "" }, { label: "抖音", href: "" }, { label: "B站", href: "" }
    ],
    qrcodes: [
      { id: "service", label: "客服微信", image: "assets/qr-wechat.jpg", description: "添加客服微信，获取更详细的框架资料。" },
      { id: "author", label: "联系作者", image: "assets/qr-wechat.jpg", description: "扫码联系作者，交流 DjangoHarness 使用与共建。" },
      { id: "group", label: "微信交流群", image: "assets/qr-wxgroup.jpg", description: "扫码加入框架交流社群。" },
      { id: "qq", label: "QQ 群", image: "", description: "扫码加入 QQ 交流群。" }
    ]
  }
};
