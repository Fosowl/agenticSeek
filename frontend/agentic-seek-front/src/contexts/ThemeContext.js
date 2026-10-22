import React, { createContext, useContext, useState, useEffect } from "react";
import { DEFAULTS, applySettings, loadSettings, saveSettings } from "../settings";

const ThemeContext = createContext();
const DARK_QUERY = "(prefers-color-scheme: dark)";

const systemIsDark = () => window.matchMedia?.(DARK_QUERY).matches ?? false;

export const ThemeProvider = ({ children }) => {
  const [settings, setSettings] = useState(loadSettings);
  const [systemDark, setSystemDark] = useState(systemIsDark);
  const isDark = settings.theme === "system" ? systemDark : settings.theme === "dark";

  // Follow the OS while the theme is "system".
  useEffect(() => {
    const media = window.matchMedia?.(DARK_QUERY);
    if (!media) return undefined;
    const onChange = (e) => setSystemDark(e.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    saveSettings(settings);
    applySettings(settings, isDark);
  }, [settings, isDark]);

  const updateSettings = (patch) => setSettings((prev) => ({ ...prev, ...patch }));
  const resetSettings = () => setSettings({ ...DEFAULTS });
  const toggleTheme = () => updateSettings({ theme: isDark ? "light" : "dark" });

  return (
    <ThemeContext.Provider
      value={{ settings, updateSettings, resetSettings, isDark, toggleTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return context;
};
