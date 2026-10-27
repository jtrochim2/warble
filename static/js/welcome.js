(() => {
  const root = document.documentElement;
  const key = 'warble-welcome-seen';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let seen = false;
  let paused = false;
  try {
    seen = localStorage.getItem(key) === '1';
    paused = localStorage.getItem('warble-motion') === 'paused';
  } catch { /* Continue without persistent browser storage. */ }
  root.dataset.welcome = seen ? 'seen' : 'first';
  let finishActive = null;

  const start = () => {
    const hero = document.querySelector('[data-welcome-hero]');
    if (!hero || seen || finishActive) return;
    seen = true;
    try { localStorage.setItem(key, '1'); } catch { /* Session-only fallback. */ }
    let timer;
    const finish = (focus = false) => {
      clearTimeout(timer);
      root.dataset.welcome = 'seen';
      if (!reduced.matches && !paused) {
        root.dataset.welcomeReveal = 'true';
        setTimeout(() => delete root.dataset.welcomeReveal, 700);
      }
      finishActive = null;
      // Only move focus in response to a deliberate skip action.
      if (focus || hero.contains(document.activeElement)) {
        const title = document.querySelector('#standings-title');
        if (title) {
          title.tabIndex = -1;
          title.focus({preventScroll: true});
        }
      }
    };
    finishActive = finish;
    if (reduced.matches || paused) finish();
    else timer = setTimeout(() => finish(), 7000);
  };
  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-welcome-skip], .skip-link') && finishActive) {
      finishActive(true);
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && finishActive) finishActive(true);
  });
  reduced.addEventListener('change', () => {
    if (reduced.matches && finishActive) finishActive();
  });
  document.addEventListener('htmx:beforeSwap', () => {
    if (finishActive) finishActive();
  });
  document.addEventListener('htmx:afterSwap', start);
  document.addEventListener('htmx:historyRestore', start);
  document.addEventListener('DOMContentLoaded', () => {
    new MutationObserver(() => {
      paused = document.body.dataset.motion === 'paused';
      if (paused && finishActive) finishActive();
    }).observe(document.body, {attributes: true, attributeFilter: ['data-motion']});
    start();
  });
})();
