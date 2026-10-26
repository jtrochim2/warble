(() => {
  const layer = document.querySelector("[data-torch-fire]");
  if (!layer) return;
  const artwork = layer.parentElement;
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const image = new Image();
  const padding = 36;
  // Flame-only regions, in the original 1672 × 941 illustration coordinates.
  const torches = [
    {x: 1006, y: 480, width: 38, height: 43, phase: 0.7},
    {x: 1286, y: 439, width: 57, height: 64, phase: 2.9},
  ];
  let ready = false;
  let frame = null;
  let lastPaint = 0;
  const clamp = (value) => Math.max(0, Math.min(1, value));

  const prepare = (torch) => {
    const texture = document.createElement("canvas");
    texture.width = torch.width;
    texture.height = torch.height;
    const context = texture.getContext("2d");
    if (!context) throw new Error("Canvas is unavailable");
    context.drawImage(image, torch.x, torch.y, torch.width, torch.height,
      0, 0, torch.width, torch.height);
    const pixels = context.getImageData(0, 0, torch.width, torch.height);
    for (let y = 0; y < torch.height; y += 1) {
      for (let x = 0; x < torch.width; x += 1) {
        const index = (y * torch.width + x) * 4;
        const [red, green, blue] = pixels.data.subarray(index, index + 3);
        const heat = clamp(Math.min((red - 165) / 80,
          (red - blue - 60) / 110, (green - 70) / 95));
        const edge = Math.sin(Math.PI * (x + 0.5) / torch.width)
          * Math.min(1, (y + 1) / 6, (torch.height - y) / 5);
        // Keep warm flame pixels; the surrounding stone and brazier stay still.
        pixels.data[index + 3] = heat < 0.18 ? 0 : 255 * heat ** 0.6 * edge;
      }
    }
    context.putImageData(pixels, 0, 0);
    torch.texture = texture;
    torch.canvas = document.createElement("canvas");
    torch.canvas.className = "torch-fire";
    torch.context = torch.canvas.getContext("2d");
    if (!torch.context) throw new Error("Canvas is unavailable");
    layer.append(torch.canvas);
  };

  const position = () => {
    if (!ready) return;
    const width = artwork.clientWidth;
    const height = artwork.clientHeight;
    const scale = Math.max(width / image.naturalWidth, height / image.naturalHeight);
    const background = getComputedStyle(artwork).backgroundPosition.split(/\s+/);
    const horizontal = parseFloat(background[0]) / 100;
    const vertical = parseFloat(background[1]) / 100;
    const offsetX = (width - image.naturalWidth * scale) * horizontal;
    const offsetY = (height - image.naturalHeight * scale) * vertical;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    for (const torch of torches) {
      const w = torch.width + padding * 2;
      const h = torch.height + padding * 2;
      Object.assign(torch.canvas.style, {
        left: `${offsetX + (torch.x - padding) * scale}px`,
        top: `${offsetY + (torch.y - padding) * scale}px`,
        width: `${w * scale}px`, height: `${h * scale}px`,
      });
      torch.canvas.width = Math.max(1, Math.ceil(w * scale * ratio));
      torch.canvas.height = Math.max(1, Math.ceil(h * scale * ratio));
      torch.context.setTransform(scale * ratio, 0, 0, scale * ratio, 0, 0);
    }
    if (!preference.matches) paint(lastPaint / 1000);
  };

  const paint = (time) => {
    for (const torch of torches) {
      const context = torch.context;
      const t = time + torch.phase;
      const flicker = 0.76 + Math.sin(t * 6.3) * 0.16 + Math.sin(t * 13.7) * 0.08;
      context.clearRect(0, 0, torch.width + padding * 2, torch.height + padding * 2);
      context.globalAlpha = 1;
      const glow = context.createRadialGradient(
        padding + torch.width / 2, padding + torch.height * 0.7, 0,
        padding + torch.width / 2, padding + torch.height * 0.7, torch.width * 1.15);
      glow.addColorStop(0, `rgba(255, 156, 42, ${flicker * 0.38})`);
      glow.addColorStop(0.45, `rgba(255, 92, 18, ${flicker * 0.12})`);
      glow.addColorStop(1, "rgba(255, 80, 10, 0)");
      context.fillStyle = glow;
      context.fillRect(0, 0, torch.width + padding * 2, torch.height + padding * 2);
      context.globalAlpha = flicker;
      for (let row = 0; row < torch.height; row += 2) {
        const tip = 1 - row / torch.height;
        const sway = (Math.sin(t * 4.1 + row * 0.17) * 4.5
          + Math.sin(t * 8.3 + row * 0.09) * 1.5) * tip;
        // Stretch upward from the fixed brazier; flame tips move most.
        const lift = -(4 + Math.sin(t * 5.7) * 3.5) * tip;
        const strip = Math.min(2, torch.height - row);
        context.drawImage(torch.texture, 0, row, torch.width, strip,
          padding + sway, padding + row + lift, torch.width, strip + 0.3);
      }
      // Small embers rise independently above each flame.
      for (let spark = 0; spark < 4; spark += 1) {
        const progress = ((t * (0.45 + spark * 0.07) + spark * 0.27) % 1);
        const x = padding + torch.width * (0.3 + spark * 0.13)
          + Math.sin(t * 2.4 + spark) * progress * 7;
        const y = padding + torch.height * 0.45 - progress * (padding + torch.height * 0.4);
        context.globalAlpha = Math.sin(progress * Math.PI) * 0.8;
        context.fillStyle = "#ffd18a";
        context.beginPath();
        context.ellipse(x, y, 0.7, 1.4, 0, 0, Math.PI * 2);
        context.fill();
      }
      context.globalAlpha = 1;
    }
  };

  const tick = (time) => {
    if (time - lastPaint >= 1000 / 24) {
      lastPaint = time;
      paint(time / 1000);
    }
    frame = requestAnimationFrame(tick);
  };

  const syncMotion = () => {
    const playing = ready && !preference.matches && !document.hidden
      && document.body.dataset.motion === "playing";
    if (playing && frame === null) frame = requestAnimationFrame(tick);
    if (!playing && frame !== null) {
      cancelAnimationFrame(frame);
      frame = null;
    }
    if (ready && preference.matches) {
      for (const torch of torches) {
        torch.context.clearRect(0, 0, torch.width + padding * 2,
          torch.height + padding * 2);
      }
    }
  };

  image.addEventListener("load", () => {
    try {
      torches.forEach(prepare);
      ready = true;
      position();
      syncMotion();
    } catch {
      // Retain the original painted fire if canvas rendering is unavailable.
      layer.hidden = true;
    }
  });
  image.addEventListener("error", () => { layer.hidden = true; });
  new MutationObserver(syncMotion).observe(document.body, {
    attributes: true, attributeFilter: ["data-motion"],
  });
  new ResizeObserver(position).observe(artwork);
  window.addEventListener("resize", position, {passive: true});
  preference.addEventListener("change", syncMotion);
  document.addEventListener("visibilitychange", syncMotion);
  image.src = layer.dataset.fireSource;
})();
