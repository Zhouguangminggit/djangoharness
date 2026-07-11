/**
 * DjangoHarness 产品介绍页 — 主逻辑
 * =====================================
 * 依赖: config.js (全局 CONFIG 对象)
 */

/* 资源路径解析：Django 模板中注入 STATIC_BASE，独立 HTML 中为空 */
function resolveAsset(path) {
  const base = window.STATIC_BASE || '';
  if (base && path && !path.startsWith('http') && !path.startsWith('/')) {
    return base + path;
  }
  return path;
}

document.addEventListener('DOMContentLoaded', () => {
  initAll();
});

function initAll() {
  renderNavbar();
  renderHero();
  renderDesign();
  renderVideo();
  renderModules();
  renderFooter();
  initQrDialog();

  initScrollAnimations();
  initNavbarScroll();
  initActiveNavLinks();
}

/* ─────────────────────────────────────────
   导航栏渲染
───────────────────────────────────────── */
function renderNavbar() {
  const { site, navbar } = CONFIG;
  const logoPath = window.SITE_LOGO || site.logo || '';

  // Logo（左上角，带图片）
  const logoEl = document.getElementById('nav-logo');
  logoEl.innerHTML = `
    ${logoPath ? `<img src="${resolveAsset(logoPath)}" alt="${site.name}" class="logo-img" onerror="this.style.display='none'">` : ''}
    <span class="nav-logo-text">${site.name}</span>
  `;
  logoEl.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  // 导航链接
  const linksEl = document.getElementById('nav-links');
  linksEl.innerHTML = navbar.links.map(l => `
    <a class="nav-link" href="${l.href}">${l.label}</a>
  `).join('');

  // 操作按钮
  const actionsEl = document.getElementById('nav-actions');
  actionsEl.innerHTML = `
    <a class="btn btn-outline nav-btn" href="${site.loginUrl}">登录</a>
    <a class="btn btn-primary nav-btn" href="${site.loginUrl}">
      开始使用
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px">
        <path d="M5 12h14M12 5l7 7-7 7"/>
      </svg>
    </a>
  `;
}

/* ─────────────────────────────────────────
   Hero 板块渲染
───────────────────────────────────────── */
function renderHero() {
  const { site, title: t } = CONFIG;

  document.getElementById('hero-badge').textContent = t.badge;

  document.getElementById('hero-title').innerHTML = `
    ${t.headline}<br>
    <span class="accent-line">${t.headlineAccent}</span>
  `;

  document.getElementById('hero-subline').textContent = t.subline;
  document.getElementById('hero-desc').textContent   = t.desc;

  document.getElementById('btn-start').href  = site.loginUrl;
  document.getElementById('btn-docs').href     = site.docsUrl;
}

/* ─────────────────────────────────────────
   Design 板块渲染 + Tab 切换
───────────────────────────────────────── */
let activeDesignIdx = 0;

function renderDesign() {
  const { design } = CONFIG;

  document.getElementById('design-label').textContent    = design.label;
  document.getElementById('design-title').textContent    = design.title;
  document.getElementById('design-subtitle').textContent = design.subtitle;

  // Tab 列表
  const tabsEl = document.getElementById('design-tabs');
  tabsEl.innerHTML = design.tabs.map((tab, i) => `
    <button class="design-tab anim d${i + 1} ${i === 0 ? 'active' : ''}"
            data-idx="${i}" type="button">
      <div class="tab-title">
        <span class="design-tab-icon">${tab.icon}</span>
        <span>${tab.label}</span>
      </div>
      <div class="tab-desc">${tab.desc}</div>
    </button>
  `).join('');

  tabsEl.querySelectorAll('.design-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.idx, 10);
      switchDesignTab(idx);
    });
  });

  renderDesignPreview(0);
}

function switchDesignTab(idx) {
  if (idx === activeDesignIdx) return;

  document.querySelectorAll('.design-tab').forEach((btn, i) => {
    btn.classList.toggle('active', i === idx);
  });

  const container = document.getElementById('design-img-container');
  const descEl    = document.getElementById('design-desc');

  container.classList.add('transitioning');
  descEl.style.opacity = '0';

  setTimeout(() => {
    activeDesignIdx = idx;
    renderDesignPreview(idx);
    container.classList.remove('transitioning');
    descEl.style.opacity = '1';
  }, 350);
}

function renderDesignPreview(idx) {
  const tab = CONFIG.design.tabs[idx];
  const container = document.getElementById('design-img-container');
  const descEl    = document.getElementById('design-desc');

  container.innerHTML = `
    <img
      src="${resolveAsset(tab.image)}"
      alt="${tab.label} 原型图"
      onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"
    >
    <div class="img-placeholder" style="display:none">
      <div class="placeholder-icon">${tab.icon}</div>
      <p>${tab.label} 原型图<br><small style="color:var(--text-muted)">请将图片放置在 assets/ 目录</small></p>
    </div>
  `;

  descEl.textContent = tab.desc;
}

/* ─────────────────────────────────────────
   Video 板块渲染
───────────────────────────────────────── */
function renderVideo() {
  const { video } = CONFIG;

  // 左侧标题
  const leftTitleEl = document.getElementById('video-left-title');
  if (video.leftTitle) {
    leftTitleEl.innerHTML = `
      <h2>${video.leftTitle.title}</h2>
      <p>${video.leftTitle.subtitle}</p>
    `;
  } else {
    leftTitleEl.style.display = 'none';
  }

  // 右侧标题
  document.getElementById('video-title').textContent = video.title;
  document.getElementById('video-brief').textContent = video.brief;

  // 视频源
  const videoEl    = document.getElementById('video-player');
  const sourceEl   = document.getElementById('video-source');
  const placeholder = document.getElementById('video-placeholder');

  if (video.videoSrc) {
    sourceEl.src = resolveAsset(video.videoSrc);
    if (video.videoPoster) videoEl.poster = resolveAsset(video.videoPoster);
    videoEl.load();
    videoEl.addEventListener('canplay', () => {
      placeholder.classList.add('has-video');
    }, { once: true });
    videoEl.addEventListener('error', () => {
      videoEl.style.display = 'none';
    }, { once: true });
  }

  // 详细说明
  const detailsEl = document.getElementById('video-details');
  detailsEl.innerHTML = video.details.map((d, i) => `
    <div class="video-detail-item anim d${i + 1}">
      <div class="vd-icon">${d.icon}</div>
      <div class="vd-text">
        <h4>${d.title}</h4>
        <p>${d.desc}</p>
      </div>
    </div>
  `).join('');
}

/* ─────────────────────────────────────────
   Module 板块渲染
───────────────────────────────────────── */
function renderModules() {
  const { modules } = CONFIG;

  document.getElementById('modules-label').textContent    = modules.label;
  document.getElementById('modules-title').textContent      = modules.title;
  document.getElementById('modules-subtitle').textContent   = modules.subtitle;

  const gridEl = document.getElementById('modules-grid');
  gridEl.innerHTML = modules.items.map((item, i) => `
    <div class="module-card anim d${(i % 3) + 1}">
      <div class="module-icon">${item.icon}</div>
      <span class="module-tag">${item.tag}</span>
      <h3 class="module-title">${item.title}</h3>
      <p class="module-desc">${item.desc}</p>
    </div>
  `).join('');
}

/* ─────────────────────────────────────────
   Footer 板块渲染
───────────────────────────────────────── */
function renderFooter() {
  const { site, footer } = CONFIG;
  const logoPath = window.SITE_LOGO || site.logo || '';

  // Logo（底部，带图片）
  document.getElementById('footer-logo').innerHTML = `
    ${logoPath ? `<img src="${resolveAsset(logoPath)}" alt="${site.name}" class="logo-img" onerror="this.style.display='none'">` : ''}
    <span class="logo-text">${site.name}</span>
  `;

  document.getElementById('footer-slogan').textContent = footer.slogan;

  // 链接
  document.getElementById('footer-links').innerHTML = footer.links.filter(l => l.href).map(l => `
    <a class="footer-link" href="${l.href}" target="_blank" rel="noopener">${l.label}</a>
  `).join('');

  // 二维码
  const qrEl = document.getElementById('footer-qrcodes');
  const visibleQrCodes = (footer.qrcodes || []).filter(qr => qr.image);
  if (visibleQrCodes.length > 0) {
    qrEl.innerHTML = visibleQrCodes.map(qr => `
      <button class="qr-item" type="button" data-qr-id="${qr.id}">
        <div class="qr-img-wrap">
          <img
            src="${resolveAsset(qr.image)}"
            alt="${qr.label}"
          >
        </div>
        <span class="qr-label">${qr.label}</span>
      </button>
    `).join('');
  } else {
    qrEl.style.display = 'none';
  }

  // 底部信息
  const authorName = footer.author.name;
  const authorEmail = footer.author.email;
  const year = new Date().getFullYear();

  document.getElementById('footer-license').textContent = `© ${year} ${footer.license}`;
  document.getElementById('footer-author').innerHTML = authorEmail
    ? `<a href="mailto:${authorEmail}" style="color:rgba(255,255,255,0.3);transition:color 0.2s"
         onmouseover="this.style.color='var(--primary)'"
         onmouseout="this.style.color='rgba(255,255,255,0.3)'">${authorName}</a>`
    : authorName;
}

function initQrDialog() {
  const modal = document.querySelector('[data-qr-modal]');
  const image = modal?.querySelector('[data-qr-image]');
  const title = modal?.querySelector('[data-qr-title]');
  const description = modal?.querySelector('[data-qr-description]');
  const closeButton = modal?.querySelector('.qr-modal__close');
  let trigger = null;

  function openDialog(id, source) {
    const qr = (CONFIG.footer.qrcodes || []).find(item => item.id === id && item.image);
    if (!qr || !modal || !image || !title || !description) return;
    trigger = source;
    image.src = resolveAsset(qr.image);
    image.alt = qr.label;
    title.textContent = qr.label;
    description.textContent = qr.description || '';
    modal.hidden = false;
    document.body.classList.add('modal-open');
    closeButton?.focus();
  }

  function closeDialog() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove('modal-open');
    trigger?.focus();
  }

  document.querySelectorAll('[data-qr-id]').forEach(button => button.addEventListener('click', () => openDialog(button.dataset.qrId, button)));
  document.querySelectorAll('[data-contact]').forEach(button => button.addEventListener('click', () => openDialog(button.dataset.contact, button)));
  modal?.querySelectorAll('[data-qr-close]').forEach(button => button.addEventListener('click', closeDialog));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeDialog();
    if (event.key === 'Tab' && modal && !modal.hidden) {
      event.preventDefault();
      closeButton?.focus();
    }
  });
}

/* ─────────────────────────────────────────
   滚动动画 (IntersectionObserver)
───────────────────────────────────────── */
function initScrollAnimations() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin: '0px 0px -60px 0px', threshold: 0.1 }
  );

  requestAnimationFrame(() => {
    document.querySelectorAll('.anim').forEach(el => observer.observe(el));
  });
}

/* ─────────────────────────────────────────
   导航栏滚动效果
───────────────────────────────────────── */
function initNavbarScroll() {
  const nav = document.getElementById('navbar');
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ─────────────────────────────────────────
   导航链接激活状态（scrollspy）
───────────────────────────────────────── */
function initActiveNavLinks() {
  const sections = ['design', 'video', 'modules'];
  const NAV_H = 80;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            link.classList.toggle('active', href === `#${id}`);
          });
        }
      });
    },
    { rootMargin: `-${NAV_H}px 0px -60% 0px`, threshold: 0 }
  );

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}
