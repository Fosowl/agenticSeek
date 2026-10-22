import React from "react";
import logo from "../logo.png";

export const ICONS = {
  code: "M8 7l-5 5 5 5M16 7l5 5-5 5",
  folder: "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  globe: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c2.5 2.7 2.5 15.3 0 18M12 3c-2.5 2.7-2.5 15.3 0 18",
  list: "M9 6h11M9 12h11M9 18h11M4 6l1 1 2-2M4 12l1 1 2-2M4 18l1 1 2-2",
  chat: "M4 5h16v11H8l-4 4z",
  panelLeft: "M4 5h16v14H4zM9.5 5v14",
  panelRight: "M4 5h16v14H4zM14.5 5v14",
  menu: "M4 7h16M4 12h16M4 17h16",
  file: "M14 3H6v18h12V7zM14 3v4h4",
  image: "M4 5h16v14H4zM4 16l5-5 4 4 3-3 4 4M15 9h.01",
  refresh: "M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7",
  key: "M15 7a4 4 0 1 1-3.87 5H9v2H7v2H4v-3l5.13-5.13A4 4 0 0 1 15 7z",
  settings: "M4 6h9M17 6h3M13 4v4M4 12h3M11 12h9M7 10v4M4 18h11M19 18h1M15 16v4",
};

export const Icon = ({ d, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d={d} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

// Backend agent names come from api.py: config.ini's agent_name (casual),
// "coder", "File Agent", "Browser" and "Planner".
export const AGENT_KINDS = [
  { kind: "casual", label: "Casual", icon: ICONS.chat },
  { kind: "coder", label: "Coder", icon: ICONS.code, test: /cod/i },
  { kind: "browser", label: "Browser", icon: ICONS.globe, test: /brows|web/i },
  { kind: "files", label: "Files", icon: ICONS.folder, test: /file/i },
  { kind: "planner", label: "Planner", icon: ICONS.list, test: /plan/i },
];

export const agentKind = (name = "") =>
  AGENT_KINDS.find(({ test }) => test?.test(name)) || AGENT_KINDS[0];

export const AgentBadge = ({ name }) => {
  const { kind, icon } = agentKind(name);
  return (
    <span className={`agent-badge agent-${kind}`}>
      <Icon d={icon} size={12} />
      {name || "Agent"}
    </span>
  );
};

// The project logo. state: "idle" | "thinking" (ripple ring) | "offline" (greyed).
export const AgentOrb = ({ state }) => (
  <span className={`orb orb-${state}`}>
    <img src={logo} alt={`AgenticSeek, agents ${state}`} draggable="false" />
  </span>
);
