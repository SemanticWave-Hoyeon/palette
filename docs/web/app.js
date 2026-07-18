"use strict";

const PRESETS = {
  none: { label: "None", colors: [] },
  npg: {
    label: "Nature Publishing Group",
    colors: ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85"],
  },
  observable: {
    label: "Observable 10",
    colors: ["#4269D0", "#EFB118", "#FF725C", "#6CC5B0", "#3CA951", "#FF8AB7", "#A463F2", "#97BBF5", "#9C6B4E", "#9498A0"],
  },
  bmj: {
    label: "BMJ",
    colors: ["#2A6EBB", "#F0AB00", "#C50084", "#7D5CC6", "#E37222", "#69BE28", "#00B2A9", "#CD202C", "#747678"],
  },
  jama: {
    label: "JAMA",
    colors: ["#374E55", "#DF8F44", "#00A1D5", "#B24745", "#79AF97", "#6A6599", "#80796B"],
  },
  science: {
    label: "Science / AAAS",
    colors: ["#3B4992", "#EE0000", "#008B45", "#631879", "#008280", "#BB0021", "#5F559B", "#A20056", "#808180", "#1B1919"],
  },
  nejm: {
    label: "NEJM",
    colors: ["#BC3C29", "#0072B5", "#E18727", "#20854E", "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97"],
  },
  lancet: {
    label: "Lancet",
    colors: ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6", "#1B1919"],
  },
  jco: {
    label: "Journal of Clinical Oncology",
    colors: ["#0073C2", "#EFC000", "#868686", "#CD534C", "#7AA6DC", "#003C67", "#8F7700", "#3B3B3B", "#A73030", "#4A6990"],
  },
  frontiers: {
    label: "Frontiers",
    colors: ["#D51317", "#F39200", "#EFD500", "#95C11F", "#007B3D", "#31B7BC", "#0094CD", "#164194", "#6F286A", "#706F6F"],
  },
  petroff6: {
    label: "Petroff Accessible 6",
    colors: ["#5790FC", "#F89C20", "#E42536", "#964A8B", "#9C9CA1", "#7A21DD"],
  },
  petroff8: {
    label: "Petroff Accessible 8",
    colors: ["#1845FB", "#FF5E02", "#C91F16", "#C849A9", "#ADAD7D", "#86C8DD", "#578DFF", "#656364"],
  },
  petroff10: {
    label: "Petroff Accessible 10",
    colors: ["#3F90DA", "#FFA90E", "#BD1F01", "#94A4A2", "#832DB6", "#A96B59", "#E76300", "#B9AC70", "#717581", "#92DADD"],
  },
};

const DEFAULT_COLORS = ["#1E88E5", "#FFC107", "#43A047", "#D81B60", "#5E35B1", "#00ACC1"];
const els = {};
const state = {
  colors: [],
  locked: [],
  editIndex: null,
  clickTimer: null,
};

function init() {
  for (const id of [
    "rollButton",
    "countInput",
    "modeSelect",
    "harmonySelect",
    "colorblindSelect",
    "backgroundSelect",
    "seedEnabled",
    "seedInput",
    "presetSelect",
    "applyPresetButton",
    "copyButton",
    "saveButton",
    "clearLocksButton",
    "paletteGrid",
    "paletteOutput",
    "previewStrip",
    "lineChart",
    "barChart",
    "pieChart",
    "metricCount",
    "metricLocked",
    "metricMode",
    "statusBar",
    "editDialog",
    "dialogColorInput",
    "dialogHexInput",
    "dialogPreview",
    "dialogApplyButton",
    "dialogClearButton",
  ]) {
    els[id] = document.getElementById(id);
  }

  populatePresets();
  setCount(6);
  bindEvents();
  rollPalette();
  window.addEventListener("resize", scheduleChartRender);
}

function populatePresets() {
  for (const [key, preset] of Object.entries(PRESETS)) {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = preset.label;
    els.presetSelect.appendChild(option);
  }
}

function bindEvents() {
  els.rollButton.addEventListener("click", rollPalette);
  els.modeSelect.addEventListener("change", updateOutput);
  els.countInput.addEventListener("change", () => setCount(readCount()));
  els.seedEnabled.addEventListener("change", () => {
    els.seedInput.disabled = !els.seedEnabled.checked;
  });
  els.applyPresetButton.addEventListener("click", applyPreset);
  els.copyButton.addEventListener("click", copyArray);
  els.saveButton.addEventListener("click", savePng);
  els.clearLocksButton.addEventListener("click", clearLocks);
  els.dialogColorInput.addEventListener("input", () => {
    const color = normalizeHex(els.dialogColorInput.value);
    els.dialogHexInput.value = color;
    updateDialogPreview(color);
  });
  els.dialogHexInput.addEventListener("input", () => {
    try {
      const color = normalizeHex(els.dialogHexInput.value);
      els.dialogColorInput.value = color.toLowerCase();
      updateDialogPreview(color);
    } catch {
      els.dialogPreview.style.background = "#ffffff";
    }
  });
  els.dialogApplyButton.addEventListener("click", applyEditedColor);
  els.dialogClearButton.addEventListener("click", clearEditedColor);
}

function readCount() {
  const value = Number.parseInt(els.countInput.value, 10);
  if (!Number.isFinite(value)) return state.colors.length || 6;
  return Math.min(24, Math.max(1, value));
}

function setCount(count) {
  els.countInput.value = String(count);
  while (state.colors.length < count) {
    const fallback = DEFAULT_COLORS[state.colors.length % DEFAULT_COLORS.length];
    state.colors.push(fallback);
    state.locked.push(false);
  }
  state.colors = state.colors.slice(0, count);
  state.locked = state.locked.slice(0, count);
  renderSwatches();
}

function rollPalette() {
  try {
    const count = readCount();
    setCount(count);
    const lockedColors = state.colors.filter((color, index) => state.locked[index] && color);
    const generated = generatePalette({
      n: count,
      mode: els.modeSelect.value,
      harmony: els.harmonySelect.value,
      colorblind: els.colorblindSelect.value || null,
      background: els.backgroundSelect.value,
      seed: currentSeed(),
      seedColors: lockedColors,
    });
    const suffix = generated.slice(lockedColors.length);
    let suffixIndex = 0;
    for (let i = 0; i < count; i += 1) {
      if (state.locked[i] && state.colors[i]) continue;
      state.colors[i] = suffix[suffixIndex];
      suffixIndex += 1;
    }
    renderSwatches();
    setStatus(`Generated a new palette${currentSeed() === null ? "" : ` with seed ${currentSeed()}`}.`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function applyPreset() {
  try {
    const key = els.presetSelect.value;
    if (key === "none") {
      setStatus("Choose a preset first.", true);
      return;
    }
    const count = readCount();
    setCount(count);
    const presetColors = PRESETS[key].colors.slice(0, count);
    const extended = generatePalette({
      n: count,
      mode: els.modeSelect.value,
      harmony: els.harmonySelect.value,
      colorblind: els.colorblindSelect.value || null,
      background: els.backgroundSelect.value,
      seed: currentSeed(),
      seedColors: presetColors,
    });
    state.colors = extended;
    const lockedCount = Math.min(PRESETS[key].colors.length, count);
    state.locked = state.colors.map((_, index) => index < lockedCount);
    renderSwatches();
    setStatus(`Applied preset: ${PRESETS[key].label}; locked ${lockedCount} preset colors.`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function currentSeed() {
  if (!els.seedEnabled.checked) return null;
  const seed = Number.parseInt(els.seedInput.value, 10);
  if (!Number.isFinite(seed) || seed < 0) {
    throw new Error("Seed must be 0 or a positive integer.");
  }
  return seed;
}

function renderSwatches() {
  els.paletteGrid.innerHTML = "";
  const count = state.colors.length;
  const columns = count <= 8 ? 4 : count <= 12 ? 4 : 6;
  els.paletteGrid.style.setProperty("--columns", String(columns));

  state.colors.forEach((color, index) => {
    const swatch = document.createElement("button");
    swatch.type = "button";
    swatch.className = `swatch${state.locked[index] ? " locked" : ""}`;
    swatch.style.background = color || "#EEF1F5";
    swatch.style.color = textColor(color);
    swatch.title = color || "Empty color";
    swatch.addEventListener("click", () => scheduleToggleLock(index));
    swatch.addEventListener("dblclick", (event) => {
      event.preventDefault();
      clearPendingClick();
      openEditor(index);
    });

    const top = document.createElement("span");
    top.className = "swatch-top";

    const number = document.createElement("span");
    number.className = "swatch-index";
    number.textContent = String(index + 1).padStart(2, "0");
    top.appendChild(number);

    const badge = document.createElement("span");
    badge.className = "lock-badge";
    badge.textContent = state.locked[index] ? "LOCKED" : "OPEN";
    top.appendChild(badge);
    swatch.appendChild(top);

    const code = document.createElement("span");
    code.className = "swatch-code";
    code.textContent = color || "EMPTY";
    swatch.appendChild(code);

    const bottom = document.createElement("span");
    bottom.className = "swatch-bottom";
    const hint = document.createElement("span");
    hint.className = "swatch-hint";
    hint.textContent = state.locked[index] ? "fixed" : "random";
    bottom.appendChild(hint);
    swatch.appendChild(bottom);
    els.paletteGrid.appendChild(swatch);
  });
  updateOutput();
}

function scheduleToggleLock(index) {
  clearPendingClick();
  state.clickTimer = window.setTimeout(() => {
    state.clickTimer = null;
    toggleLock(index);
  }, 180);
}

function clearPendingClick() {
  if (state.clickTimer !== null) {
    window.clearTimeout(state.clickTimer);
    state.clickTimer = null;
  }
}

function toggleLock(index) {
  if (!state.colors[index]) return;
  state.locked[index] = !state.locked[index];
  renderSwatches();
  setStatus(`${state.colors[index]} ${state.locked[index] ? "locked" : "unlocked"}.`);
}

function clearLocks() {
  state.locked = state.locked.map(() => false);
  renderSwatches();
  setStatus("Cleared all locks.");
}

function updateOutput() {
  const colors = state.colors.filter(Boolean);
  const locked = state.locked.filter(Boolean).length;
  els.metricCount.textContent = `${state.colors.length} ${state.colors.length === 1 ? "color" : "colors"}`;
  els.metricLocked.textContent = `${locked} locked`;
  els.metricMode.textContent = els.modeSelect.value;
  els.paletteOutput.value = pythonArray(colors);
  els.previewStrip.innerHTML = "";
  els.previewStrip.style.setProperty("--preview-count", String(Math.max(colors.length, 1)));
  for (const color of colors) {
    const item = document.createElement("span");
    item.className = "preview-swatch";
    item.style.background = color;
    els.previewStrip.appendChild(item);
  }
  renderCharts(colors);
}

let chartFrame = null;

function scheduleChartRender() {
  if (chartFrame !== null) window.cancelAnimationFrame(chartFrame);
  chartFrame = window.requestAnimationFrame(() => {
    chartFrame = null;
    renderCharts(state.colors.filter(Boolean));
  });
}

function prepareCanvas(canvas) {
  const width = Math.max(240, Math.floor(canvas.getBoundingClientRect().width));
  const height = 220;
  const scale = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(width * scale);
  canvas.height = Math.floor(height * scale);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.clearRect(0, 0, width, height);
  return { ctx, width, height };
}

function renderCharts(colors) {
  if (!els.lineChart || !els.barChart || !els.pieChart) return;
  drawLineChart(els.lineChart, colors);
  drawBarChart(els.barChart, colors);
  drawPieChart(els.pieChart, colors);
}

function drawChartFrame(ctx, width, height, padding) {
  ctx.strokeStyle = "#E2E5EA";
  ctx.lineWidth = 1;
  ctx.font = "10px Inter, system-ui, sans-serif";
  ctx.fillStyle = "#747B86";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let step = 0; step <= 4; step += 1) {
    const y = padding.top + ((height - padding.top - padding.bottom) * step) / 4;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
    ctx.fillText(String(100 - step * 25), padding.left - 7, y);
  }
}

function drawLineChart(canvas, colors) {
  const { ctx, width, height } = prepareCanvas(canvas);
  const padding = { top: 14, right: 8, bottom: 24, left: 34 };
  drawChartFrame(ctx, width, height, padding);
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const points = 6;
  colors.forEach((color, series) => {
    ctx.beginPath();
    for (let point = 0; point < points; point += 1) {
      const x = padding.left + (plotWidth * point) / (points - 1);
      const wave = 48 + 24 * Math.sin(point * 0.9 + series * 1.17) + ((series * 13 + point * 7) % 19);
      const value = Math.max(8, Math.min(94, wave));
      const y = padding.top + plotHeight * (1 - value / 100);
      if (point === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.stroke();
  });
  drawXAxisLabels(ctx, width, height, padding, ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]);
}

function drawBarChart(canvas, colors) {
  const { ctx, width, height } = prepareCanvas(canvas);
  const padding = { top: 14, right: 8, bottom: 24, left: 34 };
  drawChartFrame(ctx, width, height, padding);
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const gap = Math.max(2, Math.min(7, plotWidth / Math.max(colors.length, 1) / 4));
  const barWidth = Math.max(2, (plotWidth - gap * (colors.length + 1)) / Math.max(colors.length, 1));
  colors.forEach((color, index) => {
    const value = 34 + ((index * 23 + 31) % 61);
    const barHeight = plotHeight * (value / 100);
    const x = padding.left + gap + index * (barWidth + gap);
    const y = padding.top + plotHeight - barHeight;
    ctx.fillStyle = color;
    ctx.fillRect(x, y, barWidth, barHeight);
  });
  if (colors.length <= 12) {
    ctx.fillStyle = "#747B86";
    ctx.font = "10px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    colors.forEach((_, index) => {
      const x = padding.left + gap + index * (barWidth + gap) + barWidth / 2;
      ctx.fillText(String(index + 1), x, height - padding.bottom + 7);
    });
  }
}

function drawXAxisLabels(ctx, width, height, padding, labels) {
  if (labels.length > 12) return;
  const plotWidth = width - padding.left - padding.right;
  ctx.fillStyle = "#747B86";
  ctx.font = "10px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  labels.forEach((label, index) => {
    const denominator = Math.max(labels.length - 1, 1);
    const x = labels.length === 1
      ? padding.left + plotWidth / 2
      : padding.left + (plotWidth * index) / denominator;
    ctx.fillText(label, x, height - padding.bottom + 7);
  });
}

function drawPieChart(canvas, colors) {
  const { ctx, width, height } = prepareCanvas(canvas);
  const values = colors.map((_, index) => 3 + ((index * 7 + 5) % 11));
  const total = values.reduce((sum, value) => sum + value, 0);
  const radius = Math.min(width, height) * 0.36;
  const centerX = width / 2;
  const centerY = height / 2 + 3;
  let angle = -Math.PI / 2;
  values.forEach((value, index) => {
    const nextAngle = angle + (value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, angle, nextAngle);
    ctx.closePath();
    ctx.fillStyle = colors[index];
    ctx.fill();
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 2;
    ctx.stroke();
    angle = nextAngle;
  });
  if (!colors.length) {
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fillStyle = "#EEF1F5";
    ctx.fill();
  }
}

function openEditor(index) {
  state.editIndex = index;
  const color = normalizeHex(state.colors[index] || "#1E88E5");
  els.dialogHexInput.value = color;
  els.dialogColorInput.value = color.toLowerCase();
  updateDialogPreview(color);
  if (typeof els.editDialog.showModal === "function") {
    els.editDialog.showModal();
  } else {
    els.editDialog.setAttribute("open", "");
  }
}

function updateDialogPreview(color) {
  els.dialogPreview.style.background = color;
}

function applyEditedColor() {
  try {
    const color = normalizeHex(els.dialogHexInput.value);
    state.colors[state.editIndex] = color;
    state.locked[state.editIndex] = true;
    renderSwatches();
    els.editDialog.close();
    setStatus(`${color} set and locked.`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function clearEditedColor() {
  state.colors[state.editIndex] = null;
  state.locked[state.editIndex] = false;
  renderSwatches();
  els.editDialog.close();
  setStatus(`Color ${state.editIndex + 1} cleared.`);
}

async function copyArray() {
  const colors = state.colors.filter(Boolean);
  const text = pythonArray(colors);
  try {
    await navigator.clipboard.writeText(text);
    setStatus(`Copied ${colors.length} colors as a Python array string.`);
  } catch {
    els.paletteOutput.focus();
    els.paletteOutput.select();
    setStatus("Clipboard permission was denied; selected the Python array output.", true);
  }
}

function pythonArray(colors) {
  return `[${colors.map((color) => `"${color}"`).join(", ")}]`;
}

function savePng() {
  const colors = state.colors.filter(Boolean);
  if (!colors.length) {
    setStatus("Roll a palette first.", true);
    return;
  }
  const swatchWidth = 190;
  const swatchHeight = 122;
  const labelHeight = 34;
  const width = swatchWidth * colors.length;
  const height = swatchHeight + labelHeight;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, width, height);
  ctx.font = "16px ui-monospace, Menlo, Consolas, monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  colors.forEach((color, index) => {
    const x = index * swatchWidth;
    ctx.fillStyle = color;
    ctx.fillRect(x, 0, swatchWidth, swatchHeight);
    ctx.fillStyle = textColor(color);
    ctx.fillText(color, x + swatchWidth / 2, swatchHeight / 2);
    ctx.fillStyle = "#111827";
    ctx.fillText(color, x + swatchWidth / 2, swatchHeight + labelHeight / 2);
  });
  const link = document.createElement("a");
  link.download = `paper_palette_${new Date().toISOString().replaceAll(/[:.]/g, "-")}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
  setStatus(`Saved ${colors.length} colors as PNG.`);
}

function setStatus(message, error = false) {
  els.statusBar.textContent = message;
  els.statusBar.style.color = error ? "var(--danger)" : "var(--muted)";
}

function generatePalette({ n, mode, harmony, colorblind, background, seed, seedColors }) {
  const normalized = seedColors.map(normalizeHex);
  if (normalized.length > n) {
    throw new Error("seed_colors cannot contain more colors than n.");
  }
  if (new Set(normalized).size !== normalized.length) {
    throw new Error("seed_colors cannot contain duplicate colors.");
  }
  if (normalized.length === n) return normalized;

  const rng = seed === null ? Math.random : mulberry32(seed + n * 9973 + normalized.length * 101);
  const count = n - normalized.length;
  const generated =
    mode === "categorical"
      ? generateCategorical(count, normalized, colorblind, background, rng)
      : generateAesthetic(count, normalized, harmony, colorblind, rng);
  return normalized.concat(sortByHue(generated));
}

function generateAesthetic(count, seedColors, harmony, colorblind, rng) {
  const seedLch = seedColors.map((color) => rgbToOklch(hexToRgb(color)));
  const baseHue = seedLch.length ? circularMean(seedLch.map((lch) => lch[2])) : rng() * 360;
  const targetL = seedLch.length ? clamp(mean(seedLch.map((lch) => lch[0])), 0.5, 0.78) : 0.66;
  const targetC = seedLch.length ? clamp(mean(seedLch.map((lch) => lch[1])), 0.07, 0.19) : 0.13;
  const template = chooseHarmony(harmony, Boolean(seedLch.length), count, rng);
  const centers = harmonyHues(baseHue, template);
  const selected = [];
  const selectedLab = seedColors.map((color) => rgbToOklab(hexToRgb(color)));
  const selectedSimLab = seedColors.map((color) => simulatedLab(hexToRgb(color), colorblind));

  for (let step = 0; step < count; step += 1) {
    let best = null;
    for (let i = 0; i < 1600; i += 1) {
      const center = centers[Math.floor(rng() * centers.length)];
      const hue = wrapDegrees(center + randomNormal(rng) * (template === "analogous" ? 11 : 16));
      const lightness = clamp(targetL + randomNormal(rng) * 0.095, 0.42, 0.84);
      const chroma = clamp(targetC + randomNormal(rng) * 0.045, 0.055, 0.205);
      const rgb = oklchToRgb([lightness, chroma, hue]);
      if (!inGamut(rgb)) continue;
      const hex = rgbToHex(rgb);
      const lab = rgbToOklab(rgb);
      const simLab = simulatedLab(rgb, colorblind);
      const dist = minDistance(lab, selectedLab);
      const simDist = colorblind ? minDistance(simLab, selectedSimLab) : 1;
      if (dist < 0.03 || simDist < 0.025) continue;
      const hueScore = -Math.min(...centers.map((item) => hueDistance(hue, item))) / 180;
      const score = hueScore + dist * 1.8 + simDist * 0.8 - Math.abs(chroma - targetC) * 0.8 + rng() * 0.015;
      if (!best || score > best.score) best = { hex, lab, simLab, score };
    }
    if (!best) best = fallbackColor(selected.concat(seedColors), rng, colorblind);
    selected.push(best.hex);
    selectedLab.push(best.lab);
    selectedSimLab.push(best.simLab);
  }
  return selected;
}

function generateCategorical(count, seedColors, colorblind, background, rng) {
  const selected = [];
  const selectedLab = seedColors.map((color) => rgbToOklab(hexToRgb(color)));
  const selectedSimLab = seedColors.map((color) => simulatedLab(hexToRgb(color), colorblind));
  const pool = candidatePool(Math.max(2400, count * 650), rng, background);

  for (let step = 0; step < count; step += 1) {
    let best = null;
    for (const item of pool) {
      if (selected.includes(item.hex) || seedColors.includes(item.hex)) continue;
      const normalMin = minDistance(item.lab, selectedLab);
      const simMin = colorblind ? minDistance(item.simLab[colorblind], selectedSimLab) : normalMin;
      const lightnessScore = minLightnessDistance(item.lch, selectedLab);
      if (normalMin < 0.052 || simMin < 0.04) continue;
      const tone = background === "black" || background === "dark" ? item.lch[0] * 0.12 : (1 - item.lch[0]) * 0.05;
      const score = Math.min(normalMin, 0.22) * 2.7 + Math.min(simMin, 0.2) * 1.2 + lightnessScore * 0.35 + tone;
      if (!best || score > best.score) best = { ...item, score };
    }
    if (!best) best = fallbackColor(selected.concat(seedColors), rng, "all");
    selected.push(best.hex);
    selectedLab.push(best.lab);
    selectedSimLab.push(colorblind ? best.simLab[colorblind] : best.lab);
  }
  return selected;
}

function candidatePool(size, rng, background) {
  const pool = [];
  let guard = 0;
  while (pool.length < size && guard < size * 12) {
    guard += 1;
    const l = background === "black" || background === "dark" ? 0.52 + rng() * 0.34 : 0.43 + rng() * 0.38;
    const c = 0.065 + rng() * 0.17;
    const h = rng() * 360;
    const rgb = oklchToRgb([l, c, h]);
    if (!inGamut(rgb)) continue;
    const hex = rgbToHex(rgb);
    const lab = rgbToOklab(rgb);
    pool.push({
      hex,
      lab,
      lch: [l, c, h],
      simLab: {
        protanopia: simulatedLab(rgb, "protanopia"),
        deuteranopia: simulatedLab(rgb, "deuteranopia"),
        tritanopia: simulatedLab(rgb, "tritanopia"),
        achromatopsia: simulatedLab(rgb, "achromatopsia"),
      },
    });
  }
  return pool;
}

function fallbackColor(existing, rng, colorblind) {
  const hue = rng() * 360;
  const rgb = hslToRgb(hue / 360, 0.62, 0.56);
  const hex = rgbToHex(rgb);
  const lab = rgbToOklab(rgb);
  if (colorblind === "all") {
    return {
      hex,
      lab,
      simLab: {
        protanopia: simulatedLab(rgb, "protanopia"),
        deuteranopia: simulatedLab(rgb, "deuteranopia"),
        tritanopia: simulatedLab(rgb, "tritanopia"),
        achromatopsia: simulatedLab(rgb, "achromatopsia"),
      },
      score: 0,
    };
  }
  return { hex, lab, simLab: simulatedLab(rgb, colorblind), score: 0 };
}

function chooseHarmony(harmony, hasSeed, count, rng) {
  if (["analogous", "monochrome_accent", "split_complementary", "triadic"].includes(harmony)) return harmony;
  const options =
    harmony === "expressive"
      ? hasSeed
        ? [["analogous", 0.62], ["monochrome_accent", 0.18], ["split_complementary", 0.12], ["triadic", 0.08]]
        : [["analogous", 0.58], ["monochrome_accent", 0.18], ["split_complementary", 0.14], ["triadic", 0.1]]
      : count <= 4
        ? [["analogous", 0.76], ["monochrome_accent", 0.24]]
        : [["analogous", 0.78], ["monochrome_accent", 0.22]];
  const value = rng();
  let cumulative = 0;
  for (const [name, weight] of options) {
    cumulative += weight;
    if (value <= cumulative) return name;
  }
  return options[0][0];
}

function harmonyHues(base, template) {
  const offsets = {
    analogous: [-38, -22, -9, 0, 11, 24, 39],
    monochrome_accent: [-28, -16, -8, 0, 8, 16, 28],
    split_complementary: [-24, -10, 0, 10, 24, 150, 210],
    triadic: [-16, 0, 16, 120, 240],
  }[template];
  return offsets.map((offset) => wrapDegrees(base + offset));
}

function normalizeHex(value) {
  if (typeof value !== "string") throw new Error("Expected a HEX color string.");
  const match = value.trim().match(/^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/);
  if (!match) throw new Error(`Invalid HEX color: ${value}`);
  let body = match[1];
  if (body.length === 3) body = body.split("").map((item) => item + item).join("");
  if (body.length === 8) body = body.slice(0, 6);
  return `#${body.toUpperCase()}`;
}

function hexToRgb(hex) {
  const value = normalizeHex(hex);
  return [1, 3, 5].map((index) => parseInt(value.slice(index, index + 2), 16) / 255);
}

function rgbToHex(rgb) {
  const parts = rgb.map((value) => Math.round(clamp(value, 0, 1) * 255).toString(16).padStart(2, "0"));
  return `#${parts.join("").toUpperCase()}`;
}

function srgbToLinear(value) {
  return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
}

function linearToSrgb(value) {
  return value <= 0.0031308 ? 12.92 * value : 1.055 * value ** (1 / 2.4) - 0.055;
}

function rgbToOklab(rgb) {
  const [r, g, b] = rgb.map(srgbToLinear);
  const l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b;
  const m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b;
  const s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b;
  const l_ = Math.cbrt(l);
  const m_ = Math.cbrt(m);
  const s_ = Math.cbrt(s);
  return [
    0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
    1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_,
    0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_,
  ];
}

function oklabToRgb(lab) {
  const [L, a, b] = lab;
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.291485548 * b;
  const l = l_ ** 3;
  const m = m_ ** 3;
  const s = s_ ** 3;
  return [
    linearToSrgb(+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    linearToSrgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    linearToSrgb(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
  ];
}

function rgbToOklch(rgb) {
  const [L, a, b] = rgbToOklab(rgb);
  const C = Math.sqrt(a * a + b * b);
  const h = wrapDegrees((Math.atan2(b, a) * 180) / Math.PI);
  return [L, C, h];
}

function oklchToRgb(lch) {
  const [L, C, h] = lch;
  const radians = (h * Math.PI) / 180;
  return oklabToRgb([L, C * Math.cos(radians), C * Math.sin(radians)]);
}

function inGamut(rgb) {
  return rgb.every((value) => Number.isFinite(value) && value >= -1e-7 && value <= 1 + 1e-7);
}

function simulatedLab(rgb, mode) {
  if (!mode) return rgbToOklab(rgb);
  if (mode === "achromatopsia") {
    const linear = rgb.map(srgbToLinear);
    const lum = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
    return rgbToOklab([linearToSrgb(lum), linearToSrgb(lum), linearToSrgb(lum)]);
  }
  const matrices = {
    protanopia: [
      [0.152286, 1.052583, -0.204868],
      [0.114503, 0.786281, 0.099216],
      [-0.003882, -0.048116, 1.051998],
    ],
    deuteranopia: [
      [0.367322, 0.860646, -0.227968],
      [0.280085, 0.672501, 0.047413],
      [-0.01182, 0.04294, 0.968881],
    ],
    tritanopia: [
      [1.255528, -0.076749, -0.178779],
      [-0.078411, 0.930809, 0.147602],
      [0.004733, 0.691367, 0.3039],
    ],
  };
  const matrix = matrices[mode];
  const linear = rgb.map(srgbToLinear);
  const simulated = matrix.map((row) => row.reduce((sum, coeff, index) => sum + coeff * linear[index], 0));
  return rgbToOklab(simulated.map((value) => linearToSrgb(clamp(value, 0, 1))));
}

function sortByHue(colors) {
  return colors.slice().sort((a, b) => {
    const ha = (rgbToOklch(hexToRgb(a))[2] - 350 + 360) % 360;
    const hb = (rgbToOklch(hexToRgb(b))[2] - 350 + 360) % 360;
    return ha - hb;
  });
}

function textColor(hex) {
  if (!hex) return "#333333";
  const [r, g, b] = hexToRgb(hex);
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return luminance > 0.58 ? "#111111" : "#FFFFFF";
}

function minDistance(value, selected) {
  if (!selected.length) return 1;
  return Math.min(...selected.map((item) => distance(value, item)));
}

function minLightnessDistance(lch, selectedLab) {
  if (!selectedLab.length) return 0.2;
  const L = lch[0];
  return Math.min(...selectedLab.map((lab) => Math.abs(L - lab[0])));
}

function distance(a, b) {
  return Math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2);
}

function hueDistance(a, b) {
  return Math.abs((((a - b + 180) % 360) + 360) % 360 - 180);
}

function circularMean(values) {
  const x = mean(values.map((value) => Math.cos((value * Math.PI) / 180)));
  const y = mean(values.map((value) => Math.sin((value * Math.PI) / 180)));
  return wrapDegrees((Math.atan2(y, x) * 180) / Math.PI);
}

function randomNormal(rng) {
  const u = Math.max(rng(), Number.MIN_VALUE);
  const v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function hslToRgb(h, s, l) {
  const a = s * Math.min(l, 1 - l);
  const f = (n) => {
    const k = (n + h * 12) % 12;
    return l - a * Math.max(-1, Math.min(k - 3, Math.min(9 - k, 1)));
  };
  return [f(0), f(8), f(4)];
}

function mulberry32(seed) {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function wrapDegrees(value) {
  return ((value % 360) + 360) % 360;
}

window.addEventListener("DOMContentLoaded", init);
