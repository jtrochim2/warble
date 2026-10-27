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
    let effects = null;
    const finish = (focus = false) => {
      clearTimeout(timer);
      root.dataset.welcome = 'seen';
      delete root.dataset.welcomeScene;
      effects?.remove();
      if (!reduced.matches && !paused) {
        root.dataset.welcomeReveal = 'true';
        setTimeout(() => delete root.dataset.welcomeReveal, 700);
      }
      finishActive = null;
      // Only move focus in response to a deliberate skip action.
      if (focus || document.activeElement?.matches('[data-welcome-skip]')) {
        const title = document.querySelector('#standings-title');
        if (title) {
          title.tabIndex = -1;
          title.focus({preventScroll: !focus});
        }
      }
    };
    finishActive = finish;
    if (reduced.matches || paused) finish();
    else {
      root.dataset.welcomeScene = 'active';
      const world = document.querySelector('.world');
      if (world) {
        effects = document.createElement('div');
        effects.className = 'welcome-effects';
        effects.setAttribute('aria-hidden', 'true');
        for (let index = 0; index < 30; index += 1) {
          const spark = document.createElement('i');
          spark.style.setProperty('--spark-x', `${8 + (index * 31) % 86}%`);
          spark.style.setProperty('--spark-drift', `${(index % 7 - 3) * 22}px`);
          spark.style.setProperty('--spark-delay', `${0.25 + (index % 10) * 0.14}s`);
          spark.style.setProperty('--spark-duration', `${2.7 + (index % 5) * 0.45}s`);
          effects.append(spark);
        }
        world.append(effects);
      }
      timer = setTimeout(() => finish(), 7000);
    }
  };
  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-welcome-reset]')) {
      if (finishActive) finishActive();
      seen = false;
      try { localStorage.removeItem(key); } catch { /* Session-only fallback. */ }
      const hero = document.querySelector('[data-welcome-hero]');
      if (hero) {
        event.preventDefault();
        // Commit the settled style before restarting an active CSS sequence.
        void hero.offsetWidth;
        root.dataset.welcome = 'first';
        start();
        hero.scrollIntoView({behavior: 'instant', block: 'start'});
        hero.querySelector('[data-welcome-skip]')?.focus({preventScroll: true});
      }
      return;
    }
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
    const reset = document.querySelector('[data-welcome-reset]');
    if (reset) reset.hidden = false;
    new MutationObserver(() => {
      paused = document.body.dataset.motion === 'paused';
      if (paused && finishActive) finishActive();
    }).observe(document.body, {attributes: true, attributeFilter: ['data-motion']});
    start();
  });
})();
