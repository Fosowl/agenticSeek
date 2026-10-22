import React, { useEffect, useState } from "react";
import "./DockLayout.css";

const WIDTH_KEY = "dockWidth";
const MIN_WIDTH = 300;
const DEFAULT_WIDTH = 420;
// The chat must never be squeezed out, so the dock tops out at a share of the window.
const MAX_SHARE = 0.7;
const KEY_STEP = 24;

export const clampWidth = (value, viewport = window.innerWidth) => {
  const max = Math.max(MIN_WIDTH, Math.round(viewport * MAX_SHARE));
  const number = Number(value);
  if (value === null || !Number.isFinite(number)) return Math.min(max, DEFAULT_WIDTH);
  return Math.min(max, Math.max(MIN_WIDTH, Math.round(number)));
};

// children: [main, dock]. The dock stays mounted while closed so its state survives.
export const DockLayout = ({ children, open }) => {
  // The width the user chose. Only display is clamped to the window, so one
  // visit in a narrow window doesn't overwrite the saved width.
  const [preferred, setPreferred] = useState(() => localStorage.getItem(WIDTH_KEY));
  const [, setViewport] = useState(window.innerWidth);
  const [dragging, setDragging] = useState(false);
  const width = clampWidth(preferred);

  const choose = (value) => {
    const next = clampWidth(value);
    setPreferred(next);
    localStorage.setItem(WIDTH_KEY, String(next));
  };

  // Re-render on resize so the clamp follows the window.
  useEffect(() => {
    const onResize = () => setViewport(window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  // Pointer capture keeps the drag alive (and ending) even outside the window.
  const onPointerDown = (e) => {
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    const startX = e.clientX;
    const startWidth = width;
    const handle = e.currentTarget;
    setDragging(true);
    const onMove = (move) => choose(startWidth + startX - move.clientX);
    const onEnd = () => {
      setDragging(false);
      handle.removeEventListener("pointermove", onMove);
      handle.removeEventListener("lostpointercapture", onEnd);
    };
    handle.addEventListener("pointermove", onMove);
    handle.addEventListener("lostpointercapture", onEnd);
  };

  const onKeyDown = (e) => {
    if (e.key === "ArrowLeft") choose(width + KEY_STEP);
    if (e.key === "ArrowRight") choose(width - KEY_STEP);
  };

  return (
    <div className={`dock-layout ${open ? "dock-open" : ""} ${dragging ? "dragging" : ""}`}>
      <div className="dock-main">{children[0]}</div>
      <aside className="dock" style={{ "--dock-width": `${width}px` }}>
        <div
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize the workspace"
          aria-valuenow={width}
          aria-valuemin={MIN_WIDTH}
          tabIndex={open ? 0 : -1}
          className="dock-handle"
          onPointerDown={onPointerDown}
          onKeyDown={onKeyDown}
        />
        <div className="dock-inner">{children[1]}</div>
      </aside>
    </div>
  );
};
