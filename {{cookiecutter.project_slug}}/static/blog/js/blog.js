document.addEventListener('DOMContentLoaded', () => {
  const markdownBody = document.getElementById('markdown-body');
  if (!markdownBody || typeof window.markdownit === 'undefined') {
    return;
  }

  const raw = markdownBody.dataset.markdown;
  const md = window.markdownit({ html: false, linkify: true, typographer: true });
  markdownBody.innerHTML = md.render(raw);
});
