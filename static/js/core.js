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
