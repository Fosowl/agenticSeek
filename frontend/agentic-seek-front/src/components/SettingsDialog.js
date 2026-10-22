import React, { useLayoutEffect, useRef, useState } from "react";
import { useTheme } from "../contexts/ThemeContext";
import {
  ACCENTS,
  DARK_PALETTES,
  FONTS,
  LIGHT_PALETTES,
  MONO_FONTS,
  RADII,
  TEXT_SIZE,
  WIDTHS,
} from "../settings";
import "./SettingsDialog.css";

const TABS = [
  { value: "appearance", label: "Appearance" },
  { value: "chat", label: "Chat" },
  { value: "connection", label: "Connection" },
];

const THEMES = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "system", label: "System" },
];

const Check = () => (
  <svg className="tile-check" width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M5 12l5 5 9-10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Section = ({ title, description, children }) => (
  <section className="settings-section">
    <h3>{title}</h3>
    {description && <p className="settings-description">{description}</p>}
    {children}
  </section>
);

// Label on the left, control on the right.
const Row = ({ label, description, children }) => (
  <div className="settings-row">
    <div className="settings-row-text">
      <span className="settings-row-label">{label}</span>
      {description && <span className="settings-description">{description}</span>}
    </div>
    <div className="settings-row-control">{children}</div>
  </div>
);

const Tile = ({ selected, label, onClick, children }) => (
  <button
    type="button"
    role="radio"
    aria-checked={selected}
    aria-label={label}
    className={`tile ${selected ? "selected" : ""}`}
    onClick={onClick}
  >
    {children}
    <span className="tile-label">
      {label}
      {selected && <Check />}
    </span>
  </button>
);

const Segmented = ({ label, options, value, onChange }) => (
  <div className="segmented" role="radiogroup" aria-label={label}>
    {options.map((option) => (
      <button
        key={option.value}
        type="button"
        role="radio"
        aria-checked={value === option.value}
        className={value === option.value ? "active" : ""}
        onClick={() => onChange(option.value)}
      >
        {option.label}
      </button>
    ))}
  </div>
);

const Switch = ({ label, checked, onChange }) => (
  <label className="switch">
    <input
      type="checkbox"
      role="switch"
      aria-label={label}
      checked={checked}
      onChange={(e) => onChange(e.target.checked)}
    />
    <span className="switch-track" aria-hidden="true" />
  </label>
);

// A tiny picture of the app in a ground: sidebar, a bubble, two lines of text.
const Ground = ({ swatch: [ground, surface, ink] }) => (
  <span className="ground" style={{ background: ground }}>
    <span className="ground-side" style={{ background: surface }} />
    <span className="ground-body">
      <span className="ground-bubble" style={{ background: ink }} />
      <span className="ground-line" style={{ background: ink }} />
      <span className="ground-line short" style={{ background: ink }} />
    </span>
  </span>
);

const AppearancePane = () => {
  const { settings, updateSettings, isDark } = useTheme();
  const light = LIGHT_PALETTES.find((p) => p.value === settings.lightPalette) || LIGHT_PALETTES[0];
  const dark = DARK_PALETTES.find((p) => p.value === settings.darkPalette) || DARK_PALETTES[0];
  const themeSwatch = { light: light.swatch, dark: dark.swatch };

  return (
    <>
      <Section title="Theme">
        <div className="tile-grid cols-3" role="radiogroup" aria-label="Theme">
          {THEMES.map(({ value, label }) => (
            <Tile
              key={value}
              label={label}
              selected={settings.theme === value}
              onClick={() => updateSettings({ theme: value })}
            >
              {value === "system" ? (
                <span className="ground-split">
                  <Ground swatch={themeSwatch.light} />
                  <Ground swatch={themeSwatch.dark} />
                </span>
              ) : (
                <Ground swatch={themeSwatch[value]} />
              )}
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Accent" description="Buttons, focus rings and highlights.">
        <div className="tile-grid cols-5" role="radiogroup" aria-label="Accent">
          {ACCENTS.map((accent) => (
            <Tile
              key={accent.value}
              label={accent.label}
              selected={settings.accent === accent.value}
              onClick={() => updateSettings({ accent: accent.value })}
            >
              <span
                className="accent-chip"
                style={{ background: isDark ? accent.dark : accent.light }}
              />
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Light ground" description="The page color in the light theme.">
        <div className="tile-grid cols-5" role="radiogroup" aria-label="Light ground">
          {LIGHT_PALETTES.map((palette) => (
            <Tile
              key={palette.value}
              label={palette.label}
              selected={settings.lightPalette === palette.value}
              onClick={() => updateSettings({ lightPalette: palette.value })}
            >
              <Ground swatch={palette.swatch} />
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Dark ground" description="The same choice for the dark theme.">
        <div className="tile-grid cols-5" role="radiogroup" aria-label="Dark ground">
          {DARK_PALETTES.map((palette) => (
            <Tile
              key={palette.value}
              label={palette.label}
              selected={settings.darkPalette === palette.value}
              onClick={() => updateSettings({ darkPalette: palette.value })}
            >
              <Ground swatch={palette.swatch} />
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Interface font">
        <div className="tile-grid cols-4" role="radiogroup" aria-label="Interface font">
          {FONTS.map((font) => (
            <Tile
              key={font.value}
              label={font.label}
              selected={settings.font === font.value}
              onClick={() => updateSettings({ font: font.value })}
            >
              <span className="font-sample" style={{ fontFamily: font.stack }}>
                Ag
              </span>
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Code font" description="Code blocks, tool output and file previews.">
        <div className="tile-grid cols-4" role="radiogroup" aria-label="Code font">
          {MONO_FONTS.map((font) => (
            <Tile
              key={font.value}
              label={font.label}
              selected={settings.monoFont === font.value}
              onClick={() => updateSettings({ monoFont: font.value })}
            >
              <span className="font-sample mono" style={{ fontFamily: font.stack }}>
                {"{0O}"}
              </span>
            </Tile>
          ))}
        </div>
      </Section>

      <Section title="Layout">
        <div className="settings-card">
          <Row label="Text size" description="Messages and the prompt box.">
            <input
              type="range"
              min={TEXT_SIZE.min}
              max={TEXT_SIZE.max}
              step={0.5}
              value={settings.textSize}
              aria-label="Text size"
              onChange={(e) => updateSettings({ textSize: Number(e.target.value) })}
            />
            <span className="range-value">{settings.textSize}px</span>
          </Row>
          <Row label="Corners">
            <Segmented
              label="Corners"
              options={RADII}
              value={settings.radius}
              onChange={(radius) => updateSettings({ radius })}
            />
          </Row>
          <Row label="Chat width" description="How wide a line of conversation may run.">
            <Segmented
              label="Chat width"
              options={WIDTHS}
              value={settings.width}
              onChange={(width) => updateSettings({ width })}
            />
          </Row>
          <Row label="Reduce motion" description="Turns off animations, like the shimmer.">
            <Switch
              label="Reduce motion"
              checked={settings.reduceMotion}
              onChange={(reduceMotion) => updateSettings({ reduceMotion })}
            />
          </Row>
        </div>
      </Section>
    </>
  );
};

const ChatPane = () => {
  const { settings, updateSettings } = useTheme();
  return (
    <Section title="Messages">
      <div className="settings-card">
        <Row label="Send with" description="The other one adds a new line.">
          <Segmented
            label="Send with"
            options={[
              { value: "enter", label: "Enter" },
              { value: "ctrl-enter", label: "Ctrl + Enter" },
            ]}
            value={settings.sendWith}
            onChange={(sendWith) => updateSettings({ sendWith })}
          />
        </Row>
        <Row label="Tool activity in chat" description="The ✓ / ✕ rows under an answer.">
          <Switch
            label="Tool activity in chat"
            checked={settings.showActivity}
            onChange={(showActivity) => updateSettings({ showActivity })}
          />
        </Row>
        <Row label="Open reasoning" description="Show each answer's reasoning without a click.">
          <Switch
            label="Open reasoning"
            checked={settings.openReasoning}
            onChange={(openReasoning) => updateSettings({ openReasoning })}
          />
        </Row>
      </div>
    </Section>
  );
};

const ConnectionPane = ({ backendUrl, isOnline, hasToken, onChangeToken, onClearToken }) => (
  <>
    <Section title="Backend">
      <div className="settings-card">
        <Row label="Address" description="Set with REACT_APP_BACKEND_URL at build time.">
          <code className="settings-code">{backendUrl || "same origin"}</code>
        </Row>
        <Row label="Status">
          <span className={`status-line ${isOnline ? "idle" : "offline"}`}>
            {isOnline ? "Online" : "Offline"}
          </span>
        </Row>
      </div>
    </Section>
    <Section
      title="API token"
      description="The backend only answers requests that carry its token. It is saved in this browser only."
    >
      <div className="settings-card">
        <Row label={hasToken ? "Token saved" : "No token saved"}>
          <div className="settings-actions">
            {hasToken && (
              <button type="button" className="token-secondary" onClick={onClearToken}>
                Clear
              </button>
            )}
            <button type="button" className="token-primary" onClick={onChangeToken}>
              {hasToken ? "Change…" : "Add…"}
            </button>
          </div>
        </Row>
      </div>
    </Section>
    <p className="settings-note">
      Working on the UI without models? <code>npm run mock</code> starts a fake backend with
      the same API.
    </p>
  </>
);

export const SettingsDialog = ({ open, onClose, ...connection }) => {
  const dialogRef = useRef(null);
  // Whether the current click started on the backdrop (see onClick below).
  const pressedBackdropRef = useRef(false);
  const [tab, setTab] = useState("appearance");
  const { resetSettings } = useTheme();

  // Layout effect: closing must happen before a following prompt's autoFocus runs,
  // or focus lands behind the modal.
  useLayoutEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal?.();
    if (!open && dialog.open) dialog.close?.();
  }, [open]);

  const current = TABS.find((t) => t.value === tab);

  return (
    <dialog
      ref={dialogRef}
      className="settings-dialog"
      aria-labelledby="settings-title"
      onClose={onClose}
      // A click on the backdrop lands on the <dialog> element itself. Both the
      // press and the release must be there, so dragging the text-size slider
      // out of the dialog doesn't close it.
      onPointerDown={(e) => {
        pressedBackdropRef.current = e.target === e.currentTarget;
      }}
      onClick={(e) => {
        if (pressedBackdropRef.current && e.target === e.currentTarget) onClose();
        pressedBackdropRef.current = false;
      }}
    >
      <div className="settings-shell">
        <nav className="settings-tabs" aria-label="Settings sections">
          <p className="eyebrow">Settings</p>
          {TABS.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              className={`settings-tab ${tab === value ? "active" : ""}`}
              aria-current={tab === value ? "page" : undefined}
              onClick={() => setTab(value)}
            >
              {label}
            </button>
          ))}
          <button type="button" className="settings-reset" onClick={resetSettings}>
            Reset to defaults
          </button>
        </nav>
        <div className="settings-body">
          <header className="settings-header">
            <h2 id="settings-title">{current.label}</h2>
            <button
              type="button"
              className="icon-button ghost"
              onClick={onClose}
              aria-label="Close settings"
            >
              ×
            </button>
          </header>
          <div className="settings-scroll">
            {tab === "appearance" && <AppearancePane />}
            {tab === "chat" && <ChatPane />}
            {tab === "connection" && <ConnectionPane {...connection} />}
          </div>
        </div>
      </div>
    </dialog>
  );
};
