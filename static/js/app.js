(() => {
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 760 && e.target.closest('.nav a')) {
      document.body.classList.remove('menu-open');
    }
  });

  setTimeout(() => {
    document.querySelectorAll('.flash-stack .alert.success').forEach(el => {
      el.style.transition='opacity .35s'; el.style.opacity='0'; setTimeout(()=>el.remove(),400);
    });
  }, 4500);

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => {});
    });
  }
})();
