const motionToggle = document.querySelector("[data-motion-toggle]");
const embers = document.querySelector("[data-embers]");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (embers) {
  const fragment = document.createDocumentFragment();
  for (let index = 0; index < 22; index += 1) {
    const mote = document.createElement("span");
    mote.className = "ember";
    mote.style.setProperty("--x", `${28 + ((index * 37) % 69)}%`);
    mote.style.setProperty("--y", `${24 + ((index * 19) % 70)}%`);
    mote.style.setProperty("--size", `${index % 3 === 0 ? 3 : 2}px`);
    mote.style.setProperty("--duration", `${9 + (index % 8)}s`);
    mote.style.setProperty("--delay", `${-index * 1.7}s`);
    fragment.append(mote);
  }
  embers.append(fragment);
}

if (motionToggle) {
  let paused = reducedMotion.matches;
  try {
    paused = paused || localStorage.getItem("warble-motion") === "paused";
  } catch {
    // The scene still works when browser storage is unavailable.
  }

  const updateMotion = () => {
    document.body.dataset.motion = paused ? "paused" : "playing";
    motionToggle.setAttribute("aria-pressed", String(paused));
    const label = paused ? motionToggle.dataset.playLabel : motionToggle.dataset.pauseLabel;
    motionToggle.setAttribute("aria-label", label);
    motionToggle.querySelector("[data-motion-label]").textContent = label;
    // Respect the OS preference rather than offer a control that cannot play.
    motionToggle.hidden = reducedMotion.matches;
  };

  motionToggle.addEventListener("click", () => {
    paused = !paused;
    updateMotion();
    try {
      localStorage.setItem("warble-motion", paused ? "paused" : "playing");
    } catch {
      // Motion control does not depend on persistent storage.
    }
  });
  reducedMotion.addEventListener("change", () => {
    paused = reducedMotion.matches;
    updateMotion();
  });
  updateMotion();
}
