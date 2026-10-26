// Search the complete exported season locally; no Django endpoint is needed.
(() => {
  const siteRoot = new URL('../../', document.currentScript.src);
  const syncLanguages = () => {
    const route = location.pathname.slice(siteRoot.pathname.length)
      .replace(/^(pl|en)\//, '');
    document.querySelectorAll('.language-switch a[lang]').forEach((link) => {
      link.href = new URL(`${link.lang}/${route}${location.search}`, siteRoot).href;
    });
  };
  const filter = (value) => {
    const table = document.querySelector('.ranking-table');
    if (!table) return;
    const query = value.trim().toLocaleLowerCase();
    let matches = 0;
    table.querySelectorAll('tbody tr:not([data-static-empty])').forEach((row) => {
      const name = row.querySelector('.player-name');
      if (!name) return;
      row.hidden = !name.textContent.toLocaleLowerCase().includes(query);
      if (!row.hidden) matches += 1;
    });
    const empty = table.querySelector('[data-static-empty]');
    if (empty) empty.hidden = matches > 0;
  };
  const restore = () => {
    syncLanguages();
    const input = document.querySelector('[data-static-search] input[name="q"]');
    if (!input) return;
    input.value = new URLSearchParams(location.search).get('q') || '';
    filter(input.value);
  };
  const update = (input) => {
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    history.replaceState(history.state, '', url);
    syncLanguages();
    filter(input.value);
  };
  document.addEventListener('input', (event) => {
    if (event.target.matches('[data-static-search] input[name="q"]')) update(event.target);
  });
  document.addEventListener('submit', (event) => {
    if (!event.target.matches('[data-static-search]')) return;
    event.preventDefault();
    update(event.target.querySelector('input[name="q"]'));
  });
  document.addEventListener('htmx:afterSettle', restore);
  document.addEventListener('htmx:historyRestore', restore);
  window.addEventListener('popstate', restore);
  restore();
})();
