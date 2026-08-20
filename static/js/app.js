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

  const closeProgramBtn = document.getElementById('close-program');
  if (closeProgramBtn) {
    closeProgramBtn.addEventListener('click', async () => {
      closeProgramBtn.disabled = true;
      closeProgramBtn.textContent = '…';

      // Quando aberto pelo aplicativo Windows (PyWebView), fecha de verdade.
      try {
        if (window.pywebview && window.pywebview.api && window.pywebview.api.fechar) {
          await window.pywebview.api.fechar();
          return;
        }
      } catch (_) {}

      // Fallback para janelas que o navegador permite fechar via JavaScript.
      try {
        window.open('', '_self');
        window.close();
      } catch (_) {}

      setTimeout(() => {
        closeProgramBtn.disabled = false;
        closeProgramBtn.textContent = '✕';
        alert('Para o X fechar o programa diretamente, abra a oficina pelo atalho “Mecânica do Jairo” criado pelo instalador do aplicativo Windows.');
      }, 500);
    });
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => {});
    });
  }
})();
