function csrfToken() {
  return document.cookie
    .split("; ")
    .find((item) => item.startsWith("csrftoken="))
    ?.split("=")[1];
}

document.querySelectorAll("[data-code-button]").forEach((button) => {
  button.addEventListener("click", async () => {
    const input = document.getElementById(button.dataset.target);
    if (!input?.value) {
      input?.focus();
      return;
    }
    button.disabled = true;
    const field = button.dataset.target === "id_phone" ? "phone" : "email";
    const body = new URLSearchParams({ [field]: input.value });
    try {
      const response = await fetch(button.dataset.endpoint, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken() || "" },
        body,
      });
      const payload = await response.json();
      button.textContent = payload.message;
      if (!response.ok) throw new Error(payload.message);
      let seconds = 60;
      const timer = window.setInterval(() => {
        seconds -= 1;
        button.textContent = `${seconds} 秒后重试`;
        if (seconds <= 0) {
          window.clearInterval(timer);
          button.disabled = false;
          button.textContent = "重新获取";
        }
      }, 1000);
    } catch (error) {
      button.disabled = false;
      button.textContent = error.message || "发送失败，请重试";
    }
  });
});
