// Keep the world, header, and join dialog mounted while switching seasons.
const seasonRequests = new WeakMap();

document.addEventListener("htmx:beforeRequest", (event) => {
  if (event.detail.elt.closest(".season-picker")) {
    seasonRequests.set(event.detail.xhr, null);
  }
});

document.addEventListener("htmx:beforeSwap", (event) => {
  if (seasonRequests.has(event.detail.xhr)) {
    // Capture at swap time so scrolling while the request loads is respected.
    seasonRequests.set(event.detail.xhr, {x: window.scrollX, y: window.scrollY});
  }
});

document.addEventListener("htmx:afterSwap", (event) => {
  const position = seasonRequests.get(event.detail.xhr);
  if (position) {
    window.scrollTo({left: position.x, top: position.y, behavior: "instant"});
    seasonRequests.delete(event.detail.xhr);
  }
});

const syncLanguageReturnUrl = () => {
  const next = document.querySelector(".language-switch input[name='next']");
  if (next) next.value = window.location.pathname + window.location.search;
};

for (const event of [
  "htmx:pushedIntoHistory",
  "htmx:replacedInHistory",
  "htmx:historyRestore",
]) {
  document.addEventListener(event, syncLanguageReturnUrl);
}
