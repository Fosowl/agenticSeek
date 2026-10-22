/**
 * Frontend settings: what the choices are, and how each one reaches the page.
 *
 * Every option must change something visible. Each is stamped on <html> as a
 * CSS variable the stylesheets read or a data attribute a rule keys off, so no
 * component has to opt in. Adapted from the appearance settings of Inertia
 * (github.com/nettanvirdev/inertia, MIT).
 */

export const STORAGE_KEY = "agenticseek_settings";

export const DEFAULTS = {
  theme: "system", // "light" | "dark" | "system"
  accent: "violet",
  lightPalette: "paper",
  darkPalette: "graphite",
  font: "inter",
  monoFont: "system",
  textSize: 15,
  radius: "soft",
  width: "comfortable",
  reduceMotion: false,
  sendWith: "enter", // "enter" | "ctrl-enter"
  showActivity: true,
  openReasoning: false,
};

// `light` and `dark` are the accent in each theme; `on` is the readable text on it.
export const ACCENTS = [
  { value: "violet", label: "Violet", light: "#6d28d9", dark: "#a78bfa", on: ["#ffffff", "#1b0f36"] },
  { value: "blue", label: "Blue", light: "#1d4ed8", dark: "#60a5fa", on: ["#ffffff", "#0a1834"] },
  { value: "emerald", label: "Emerald", light: "#047857", dark: "#34d399", on: ["#ffffff", "#06251b"] },
  { value: "orange", label: "Ember", light: "#c2410c", dark: "#fb923c", on: ["#ffffff", "#2b1203"] },
  { value: "rose", label: "Rose", light: "#be123c", dark: "#fb7185", on: ["#ffffff", "#37060f"] },
  { value: "cyan", label: "Cyan", light: "#0e7490", dark: "#22d3ee", on: ["#ffffff", "#04252c"] },
  { value: "amber", label: "Amber", light: "#b45309", dark: "#fbbf24", on: ["#ffffff", "#2b1a00"] },
  { value: "fuchsia", label: "Fuchsia", light: "#a21caf", dark: "#e879f9", on: ["#ffffff", "#2c0733"] },
  { value: "indigo", label: "Indigo", light: "#4338ca", dark: "#818cf8", on: ["#ffffff", "#131238"] },
  { value: "slate", label: "Slate", light: "#334155", dark: "#94a3b8", on: ["#ffffff", "#0d1420"] },
];

// The grounds. Their tokens live in globals.css; `swatch` paints the picker tile.
export const LIGHT_PALETTES = [
  { value: "paper", label: "Paper", swatch: ["#f4f1ec", "#fbfaf7", "#1b1916"] },
  { value: "snow", label: "Snow", swatch: ["#f7f8fa", "#ffffff", "#1d2024"] },
  { value: "sepia", label: "Sepia", swatch: ["#f3ead9", "#f9f3e7", "#3b3229"] },
  { value: "mist", label: "Mist", swatch: ["#eceef1", "#ffffff", "#2f3336"] },
  { value: "sage", label: "Sage", swatch: ["#eef2ec", "#f8faf6", "#2f352d"] },
];

export const DARK_PALETTES = [
  { value: "graphite", label: "Graphite", swatch: ["#161513", "#1e1c1a", "#f1ede6"] },
  { value: "midnight", label: "Midnight", swatch: ["#10131a", "#181c25", "#e4e8f0"] },
  { value: "ink", label: "Ink", swatch: ["#0a0a0a", "#141414", "#e6e6e6"] },
  { value: "ocean", label: "Ocean", swatch: ["#0d181d", "#152227", "#dbe9ee"] },
  { value: "plum", label: "Plum", swatch: ["#15111b", "#1e1925", "#e7e1ee"] },
];

// Inter and JetBrains Mono are loaded in public/index.html; the rest are system stacks.
export const FONTS = [
  { value: "inter", label: "Inter", stack: 'Inter, ui-sans-serif, system-ui, "Segoe UI", sans-serif' },
  { value: "system", label: "System", stack: 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif' },
  { value: "grotesk", label: "Grotesk", stack: '"Helvetica Neue", Arial, "Segoe UI", Roboto, sans-serif' },
  { value: "serif", label: "Serif", stack: 'Charter, "Iowan Old Style", Georgia, "Times New Roman", serif' },
];

export const MONO_FONTS = [
  { value: "system", label: "System", stack: 'ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace' },
  { value: "jetbrains", label: "JetBrains", stack: '"JetBrains Mono", ui-monospace, Consolas, monospace' },
  { value: "consolas", label: "Consolas", stack: 'Consolas, "Cascadia Mono", ui-monospace, monospace' },
  { value: "courier", label: "Courier", stack: '"Courier New", Courier, ui-monospace, monospace' },
];

export const RADII = [
  { value: "sharp", label: "Sharp", px: 6 },
  { value: "soft", label: "Soft", px: 14 },
  { value: "round", label: "Round", px: 22 },
];

export const WIDTHS = [
  { value: "narrow", label: "Narrow", css: "640px" },
  { value: "comfortable", label: "Comfortable", css: "780px" },
  { value: "wide", label: "Wide", css: "1000px" },
];

export const TEXT_SIZE = { min: 13, max: 18 };

const pick = (list, value) => list.find((entry) => entry.value === value) || list[0];

/** Saved settings merged over the defaults; anything unreadable falls back. */
export function loadSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && typeof saved === "object") return { ...DEFAULTS, ...saved };
  } catch {
    // Corrupt JSON: start from the defaults.
  }
  // The old UI saved only the theme, under "theme".
  const legacyTheme = localStorage.getItem("theme");
  return legacyTheme ? { ...DEFAULTS, theme: legacyTheme } : { ...DEFAULTS };
}

export const saveSettings = (settings) =>
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));

/** Puts every appearance choice on <html>. `isDark` is the resolved theme. */
export function applySettings(settings, isDark, root = document.documentElement) {
  const s = { ...DEFAULTS, ...settings };
  const { style, dataset } = root;

  dataset.theme = isDark ? "dark" : "light";
  dataset.lightPalette = pick(LIGHT_PALETTES, s.lightPalette).value;
  dataset.darkPalette = pick(DARK_PALETTES, s.darkPalette).value;

  const accent = pick(ACCENTS, s.accent);
  style.setProperty("--accent", isDark ? accent.dark : accent.light);
  style.setProperty("--accent-foreground", accent.on[isDark ? 1 : 0]);

  style.setProperty("--font-sans", pick(FONTS, s.font).stack);
  style.setProperty("--font-mono", pick(MONO_FONTS, s.monoFont).stack);
  const size = Math.min(TEXT_SIZE.max, Math.max(TEXT_SIZE.min, Number(s.textSize) || DEFAULTS.textSize));
  style.setProperty("--chat-font-size", `${size}px`);
  style.setProperty("--radius", `${pick(RADII, s.radius).px}px`);
  style.setProperty("--chat-width", pick(WIDTHS, s.width).css);

  if (s.reduceMotion) dataset.reduceMotion = "true";
  else delete dataset.reduceMotion;
}
