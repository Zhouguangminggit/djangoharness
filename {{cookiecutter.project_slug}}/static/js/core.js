document.documentElement.classList.add("js-ready");

function dismissMessage(message) {
  if (!message || message.classList.contains("message--leaving")) return;
  message.classList.add("message--leaving");
  window.setTimeout(() => {
    const container = message.parentElement;
    message.remove();
    if (container && !container.querySelector("[data-message]")) container.remove();
  }, 220);
}

document.querySelectorAll("[data-message]").forEach((message) => {
  const closeButton = message.querySelector("[data-message-close]");
  closeButton?.addEventListener("click", () => dismissMessage(message));

  const timeout = Number.parseInt(message.dataset.autoDismiss || "", 10);
  if (Number.isFinite(timeout) && timeout > 0) {
    window.setTimeout(() => dismissMessage(message), timeout);
  }
});

const userMenu = document.querySelector("[data-user-menu]");
const userMenuToggle = userMenu?.querySelector("[data-user-menu-toggle]");
const userMenuPanel = userMenu?.querySelector("[data-user-menu-panel]");

function closeUserMenu() {
  if (!userMenuToggle || !userMenuPanel) return;
  userMenuToggle.setAttribute("aria-expanded", "false");
  userMenuPanel.hidden = true;
}

userMenuToggle?.addEventListener("click", () => {
  const open = userMenuToggle.getAttribute("aria-expanded") === "true";
  userMenuToggle.setAttribute("aria-expanded", String(!open));
  if (userMenuPanel) userMenuPanel.hidden = open;
  if (!open) userMenuPanel?.querySelector("[role='menuitem']")?.focus();
});

document.addEventListener("click", (event) => {
  if (userMenu && !userMenu.contains(event.target)) closeUserMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeUserMenu();
    userMenuToggle?.focus();
  }
});

const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
navToggle?.addEventListener("click", () => {
  const open = navToggle.getAttribute("aria-expanded") === "true";
  navToggle.setAttribute("aria-expanded", String(!open));
  siteNav?.classList.toggle("site-nav--open", !open);
});
