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

  const fullscreenBtn = document.getElementById('fullscreen-toggle');
  const updateFullscreenLabel = () => {
    if (!fullscreenBtn) return;
    fullscreenBtn.textContent = document.fullscreenElement ? '↙ Sair da tela cheia' : '⛶ Tela cheia';
  };

  const enterFullscreen = async () => {
    if (document.fullscreenElement) return;
    const el = document.documentElement;
    if (!el.requestFullscreen) return;
    try {
      await el.requestFullscreen({ navigationUI: 'hide' });
    } catch (_) {
      try { await el.requestFullscreen(); } catch (_) {}
    }
  };

  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      if (document.fullscreenElement) {
        try { await document.exitFullscreen(); } catch (_) {}
      } else {
        await enterFullscreen();
      }
      updateFullscreenLabel();
    });
  }
  document.addEventListener('fullscreenchange', updateFullscreenLabel);
  updateFullscreenLabel();

  // Quando instalado como aplicativo, o manifest pede modo fullscreen.
  // Em navegadores que ainda exigem um gesto do usuário, a primeira interação
  // tenta completar a entrada em tela cheia automaticamente.
  const installedMode = window.matchMedia('(display-mode: standalone)').matches ||
                        window.matchMedia('(display-mode: fullscreen)').matches ||
                        window.navigator.standalone === true;
  if (installedMode && document.body.classList.contains('app-shell') && !document.fullscreenElement) {
    const firstGesture = () => enterFullscreen();
    document.addEventListener('pointerdown', firstGesture, { once: true, capture: true });
    document.addEventListener('keydown', firstGesture, { once: true, capture: true });
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js').catch(() => {});
    });
  }
})();
