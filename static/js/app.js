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
    closeProgramBtn.addEventListener('click', () => {
      try { window.close(); } catch (_) {}
      setTimeout(() => {
        document.body.innerHTML = `
          <div style="min-height:100vh;display:grid;place-items:center;background:#0b1220;color:#fff;font-family:Inter,Arial,sans-serif;text-align:center;padding:30px">
            <div>
              <div style="font-size:54px;margin-bottom:14px">✓</div>
              <h1 style="margin:0 0 8px;font-size:28px">Programa encerrado</h1>
              <p style="margin:0;color:#b8c4d6;font-size:15px">Se esta janela continuar aberta, pressione <strong>Alt + F4</strong>.</p>
            </div>
          </div>`;
      }, 300);
    });
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => {});
    });
  }
})();
