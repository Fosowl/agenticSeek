import { DEFAULTS, STORAGE_KEY, applySettings, loadSettings } from "./settings";

beforeEach(() => localStorage.clear());

test("applySettings stamps every appearance choice on the root element", () => {
  const root = document.createElement("html");
  applySettings({ accent: "blue", radius: "sharp", width: "wide", textSize: 99, reduceMotion: true }, true, root);

  expect(root.dataset.theme).toBe("dark");
  expect(root.style.getPropertyValue("--accent")).toBe("#60a5fa"); // the dark-theme blue
  expect(root.style.getPropertyValue("--radius")).toBe("6px");
  expect(root.style.getPropertyValue("--chat-width")).toBe("1000px");
  expect(root.style.getPropertyValue("--chat-font-size")).toBe("18px"); // clamped
  expect(root.dataset.reduceMotion).toBe("true");

  applySettings({ reduceMotion: false, accent: "not-a-color" }, false, root);
  expect(root.dataset.reduceMotion).toBeUndefined();
  expect(root.style.getPropertyValue("--accent")).toBe("#6d28d9"); // unknown -> first accent
});

test("loadSettings falls back to defaults and migrates the old theme key", () => {
  expect(loadSettings()).toEqual(DEFAULTS);

  localStorage.setItem("theme", "dark");
  expect(loadSettings().theme).toBe("dark");

  localStorage.setItem(STORAGE_KEY, "{not json");
  expect(loadSettings().theme).toBe("dark");

  localStorage.setItem(STORAGE_KEY, JSON.stringify({ accent: "rose" }));
  expect(loadSettings()).toEqual({ ...DEFAULTS, accent: "rose" });
});
