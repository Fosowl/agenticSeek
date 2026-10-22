import React, { useState, useEffect, useRef, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import "./App.css";
import { ThemeToggle } from "./components/ThemeToggle";
import { DockLayout } from "./components/DockLayout";
import { SettingsDialog } from "./components/SettingsDialog";
import { useTheme } from "./contexts/ThemeContext";
import { FileExplorer } from "./components/FileExplorer";
import { TokenPrompt } from "./components/TokenPrompt";
import { AgentBadge, AgentOrb, ICONS, Icon } from "./components/Agent";
import faviconPng from "./logo.png";
import { clearToken, getToken, onAuthRequired, saveToken } from "./apiAuth";
import { groupBlocks, markSeen, takeNewBlocks } from "./blocks";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
console.log("Using backend URL:", BACKEND_URL);

const SUGGESTIONS = [
  "Search the web for the latest AI agent news",
  "Write a Python script that renames my photos by date",
  "List the files in my workspace and summarize them",
  "Plan a 3-day trip to Tokyo",
];
const VIEWS = [
  { key: "blocks", label: "Editor", icon: ICONS.code },
  { key: "screenshot", label: "Browser", icon: ICONS.globe },
  { key: "files", label: "Files", icon: ICONS.folder },
];
// Tool runs shown under an answer; the rest stay in the Editor view.
const MAX_ACTIVITY_ROWS = 4;
const PHONE_QUERY = "(max-width: 768px)";
// Touch keyboards have no Shift, so there Enter adds a line and the button sends.
const isTouch = () => window.matchMedia?.("(pointer: coarse)").matches ?? false;

function App() {
  const { settings } = useTheme();
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState("blocks");
  // Desktop: the workspace panel beside the chat, closed by default.
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  // Phones show one pane at a time: "chat" or "workspace".
  const [mobileView, setMobileView] = useState("chat");
  const [isPhone, setIsPhone] = useState(() => window.matchMedia?.(PHONE_QUERY).matches ?? false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [responseData, setResponseData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [status, setStatus] = useState("Agents ready");
  // Messages whose reasoning was toggled away from the "Open reasoning" setting.
  const [expandedReasoning, setExpandedReasoning] = useState(new Set());
  // null, or why the token prompt is open: "required", "rejected", "change".
  const [tokenPrompt, setTokenPrompt] = useState(null);
  // Files picked with the paperclip, uploaded when the query is sent.
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  // Files dragged over the window; a counter because dragenter/leave fire per child.
  const [dragging, setDragging] = useState(false);
  const dragDepthRef = useRef(0);
  const textareaRef = useRef(null);
  const authRequired = tokenPrompt === "required" || tokenPrompt === "rejected";
  const messagesEndRef = useRef(null);
  // Normalized texts of agent answers already shown. A ref (not `messages`)
  // because polls overlap when the backend is slow: every in-flight response
  // must see answers appended by responses that resolved before it.
  const seenAnswersRef = useRef(new Set());
  // Tool blocks already shown (see blocks.js). null until the first poll: if
  // nothing was sent from this page yet, what exists then is history.
  const seenBlocksRef = useRef(null);
  const sentQueryRef = useRef(false);

  const fetchLatestAnswer = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/latest_answer`);
      const data = res.data;

      updateData(data);
      const blocks = Object.values(data.blocks || {});
      if (seenBlocksRef.current === null) {
        seenBlocksRef.current = new Map();
        if (!sentQueryRef.current) markSeen(seenBlocksRef.current, blocks);
      }
      if (!data.answer || data.answer.trim() === "") {
        return;
      }
      const normalizedNewAnswer = normalizeAnswer(data.answer);
      if (seenAnswersRef.current.has(normalizedNewAnswer)) {
        return;
      }
      seenAnswersRef.current.add(normalizedNewAnswer);
      const newBlocks = takeNewBlocks(seenBlocksRef.current, blocks);
      setMessages((prev) => [
        ...prev,
        {
          type: "agent",
          content: data.answer,
          reasoning: data.reasoning,
          agentName: data.agent_name,
          status: data.status,
          uid: data.uid,
          blocks: newBlocks,
        },
      ]);
      setStatus(data.status);
    } catch (error) {
      console.error("Error fetching latest answer:", error);
    }
  }, []);

  useEffect(
    () =>
      onAuthRequired(({ tokenRejected }) =>
        setTokenPrompt(tokenRejected ? "rejected" : "required")
      ),
    []
  );

  useEffect(() => {
    const intervalId = setInterval(() => {
      checkHealth();
      // /health is public; the other calls would only 401 until a token is saved.
      if (authRequired) return;
      fetchLatestAnswer();
      fetchScreenshot();
    }, 3000);
    return () => clearInterval(intervalId);
  }, [fetchLatestAnswer, authRequired]);

  useEffect(() => {
    const media = window.matchMedia?.(PHONE_QUERY);
    if (!media) return undefined;
    const onChange = (e) => setIsPhone(e.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  // A token prompt must never open behind the (modal) Settings dialog.
  useEffect(() => {
    if (authRequired) setSettingsOpen(false);
  }, [authRequired]);

  // Keep the newest message (answer, error or the thinking row) in view.
  useEffect(() => {
    // Optional call: jsdom (the tests) has no scrollIntoView.
    messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages.length, isLoading]);

  // Grow the prompt box with its content, up to the CSS max-height.
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [query]);

  const checkHealth = async () => {
    try {
      await axios.get(`${BACKEND_URL}/health`);
      setIsOnline(true);
      console.log("System is online");
    } catch {
      setIsOnline(false);
      console.log("System is offline");
    }
  };

  const fetchScreenshot = async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/screenshot`, {
        params: { timestamp: new Date().getTime() },
        responseType: "blob",
      });
      console.log("Screenshot fetched successfully");
      const imageUrl = URL.createObjectURL(res.data);
      setResponseData((prev) => {
        if (prev?.screenshot) URL.revokeObjectURL(prev.screenshot);
        return { ...prev, screenshot: imageUrl };
      });
    } catch (err) {
      console.error("Error fetching screenshot:", err);
      setResponseData((prev) => {
        if (prev?.screenshot) URL.revokeObjectURL(prev.screenshot);
        return { ...prev, screenshot: null };
      });
    }
  };

  const normalizeAnswer = (answer) => {
    return answer
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ")
      .replace(/[.,!?]/g, "");
  };


  const toggleReasoning = (messageIndex) => {
    setExpandedReasoning((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(messageIndex)) {
        newSet.delete(messageIndex);
      } else {
        newSet.add(messageIndex);
      }
      return newSet;
    });
  };

  const updateData = (data) => {
    setResponseData((prev) => ({
      ...prev,
      blocks: data.blocks || prev?.blocks || null,
      done: data.done,
      answer: data.answer,
      agent_name: data.agent_name,
      status: data.status,
      uid: data.uid,
    }));
  };

  const handleStop = async (e) => {
    e.preventDefault();
    checkHealth();
    setError(null);
    // isLoading stays on until /query returns: the agent stops between steps.
    try {
      await axios.get(`${BACKEND_URL}/stop`);
      setStatus("Requesting stop...");
    } catch (err) {
      console.error("Error stopping the agent:", err);
    }
  };

  const addAttachments = (files) =>
    setAttachments((prev) => [...prev, ...Array.from(files || [])]);

  const handleAttach = (e) => {
    addAttachments(e.target.files);
    // Reset so picking the same file again fires onChange.
    e.target.value = "";
  };

  // Drag and drop anywhere in the app adds to the same attachments as the paperclip.
  const isFileDrag = (e) => Array.from(e.dataTransfer?.types || []).includes("Files");

  const handleDragEnter = (e) => {
    if (!isFileDrag(e)) return;
    e.preventDefault();
    dragDepthRef.current += 1;
    setDragging(true);
  };

  const handleDragOver = (e) => {
    if (!isFileDrag(e)) return;
    // Without preventDefault the browser opens the file instead of dropping it.
    e.preventDefault();
    e.dataTransfer.dropEffect = isLoading ? "none" : "copy";
  };

  const handleDragLeave = (e) => {
    if (!isFileDrag(e)) return;
    dragDepthRef.current = Math.max(0, dragDepthRef.current - 1);
    if (dragDepthRef.current === 0) setDragging(false);
  };

  const handleDrop = (e) => {
    if (!isFileDrag(e)) return;
    e.preventDefault();
    dragDepthRef.current = 0;
    setDragging(false);
    if (isLoading) return;
    addAttachments(e.dataTransfer.files);
    setMobileView("chat");
    textareaRef.current?.focus();
  };

  const removeAttachment = (index) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  // Returns the workspace paths of the saved files, or null on failure.
  const uploadAttachments = async (files) => {
    if (files.length === 0) return [];
    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    try {
      const res = await axios.post(`${BACKEND_URL}/files/upload`, form);
      return res.data.paths;
    } catch (err) {
      console.error("Upload error:", err);
      const detail = err.response?.data?.detail || "Unable to upload files.";
      setMessages((prev) => [
        ...prev,
        { type: "error", content: `Upload failed: ${detail}` },
      ]);
      return null;
    }
  };

  // The agent learns the saved paths from a <files> tag after the prompt.
  const withFilesTag = (text, paths) =>
    paths.length > 0 ? `${text} <files>${paths.join(", ")}</files>` : text;

  const handleSubmit = async (e) => {
    e.preventDefault();
    checkHealth();
    if (!query.trim() || isLoading) {
      console.log("Empty query");
      return;
    }
    setIsLoading(true);
    sentQueryRef.current = true;
    setError(null);
    // The backend only reports a new status with a new answer.
    setStatus("Working…");
    // On upload failure keep the typed query and the attachments for a retry.
    const paths = await uploadAttachments(attachments);
    if (paths === null) {
      setIsLoading(false);
      return;
    }
    setMessages((prev) => [
      ...prev,
      { type: "user", content: query, files: attachments.map((file) => file.name) },
    ]);
    setAttachments([]);

    const fullQuery = withFilesTag(query, paths);
    let retryQuery = "";
    try {
      console.log("Sending query:", fullQuery);
      setQuery("");
      const res = await axios.post(`${BACKEND_URL}/query`, {
        query: fullQuery,
        tts_enabled: false,
      });
      console.log("Response:", res.data);
      const data = res.data;
      updateData(data);
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to process query.");
      setMessages((prev) => [
        ...prev,
        { type: "error", content: "Error: Unable to get a response." },
      ]);
      // Files are already saved; a retry resends their tag.
      retryQuery = fullQuery;
    } finally {
      console.log("Query completed");
      setIsLoading(false);
      setQuery(retryQuery);
    }
  };

  // Enter (or Ctrl/Cmd+Enter, per Settings) sends; IME composition is left alone.
  // keyCode 229: Safari's Enter that confirms an IME word has isComposing false.
  const handleKeyDown = (e) => {
    if (e.key !== "Enter" || e.nativeEvent.isComposing || e.keyCode === 229) return;
    const withModifier = e.ctrlKey || e.metaKey;
    const sends =
      settings.sendWith === "ctrl-enter"
        ? withModifier
        : !e.shiftKey && !withModifier && !isTouch();
    if (sends) handleSubmit(e);
  };

  const pickSuggestion = (text) => {
    setQuery(text);
    textareaRef.current?.focus();
  };

  const handleSaveToken = (token) => {
    saveToken(token);
    setTokenPrompt(null);
    // Try the token right away: a 401 reopens the prompt as "rejected".
    fetchLatestAnswer();
  };

  const handleClearToken = () => {
    clearToken();
    setTokenPrompt(null);
  };

  // The settings <dialog> sits in the top layer, above the token prompt, so
  // both of these close it.
  const changeTokenFromSettings = () => {
    setSettingsOpen(false);
    setTokenPrompt("change");
  };

  const clearTokenFromSettings = () => {
    clearToken();
    setSettingsOpen(false);
  };

  const showView = (key) => {
    setCurrentView(key);
    setWorkspaceOpen(true);
    setMobileView("workspace");
  };

  const orbState = !isOnline ? "offline" : isLoading ? "thinking" : "idle";
  const statusText = !isOnline ? "Offline" : isLoading ? status : "Online";
  const blockGroups = groupBlocks(Object.values(responseData?.blocks || {}));
  const workspaceVisible = isPhone ? mobileView === "workspace" : workspaceOpen;

  // "ran", "failed", or "2 ok · 1 failed" for a command that ran several times.
  const runsSummary = (runs) => {
    const failed = runs.filter((run) => !run.success).length;
    if (failed === 0) return "ran";
    if (failed === runs.length) return "failed";
    return `${runs.length - failed} ok · ${failed} failed`;
  };

  // Every run of one command: its number, result and output.
  const renderRuns = (runs, outputClass) => (
    <ol className="runs">
      {runs.map((run, i) => (
        <li key={i} className="run">
          <span className="run-head">
            <span className="run-label">Run {i + 1}</span>
            <span className={`pill ${run.success ? "ok" : "fail"}`}>
              {run.success ? "ok" : "failed"}
            </span>
          </span>
          {run.feedback && <pre className={outputClass}>{run.feedback}</pre>}
        </li>
      ))}
    </ol>
  );

  const renderActivity = (msgBlocks = []) => {
    if (!settings.showActivity || msgBlocks.length === 0) return null;
    const groups = groupBlocks(msgBlocks);
    const hidden = groups.length - MAX_ACTIVITY_ROWS;
    return (
      <div className="activity-list">
        {groups.slice(-MAX_ACTIVITY_ROWS).map((group, i) => {
          const last = group.runs[group.runs.length - 1];
          return (
            <details key={i} className="activity">
              <summary>
                <span className={`activity-mark ${last.success ? "ok" : "fail"}`} aria-hidden="true">
                  {last.success ? "✓" : "✕"}
                </span>
                <span className="activity-tool">{group.tool_type}</span>
                <span className="activity-result">{runsSummary(group.runs)}</span>
                {group.runs.length > 1 && (
                  <span className="runs-count">{group.runs.length} runs</span>
                )}
              </summary>
              <pre className="activity-code">{group.block}</pre>
              {group.runs.length > 1
                ? renderRuns(group.runs, "activity-feedback")
                : last.feedback && <pre className="activity-feedback">{last.feedback}</pre>}
            </details>
          );
        })}
        {hidden > 0 && (
          <button type="button" className="activity-more" onClick={() => showView("blocks")}>
            +{hidden} earlier in Editor
          </button>
        )}
      </div>
    );
  };

  const renderMessage = (msg, index) => {
    if (msg.type === "user") {
      return (
        <div key={index} className="message user-message">
          <div className="bubble">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
            {msg.files?.length > 0 && (
              <ul className="message-files">
                {msg.files.map((name, fileIndex) => (
                  <li key={fileIndex}>📎 {name}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      );
    }
    if (msg.type === "agent") {
      const showReasoning = settings.openReasoning !== expandedReasoning.has(index);
      return (
        <div key={index} className="message agent-message">
          <div className="message-meta">
            <AgentBadge name={msg.agentName} />
            {msg.reasoning && (
              <button
                type="button"
                className="reasoning-toggle"
                onClick={() => toggleReasoning(index)}
                aria-expanded={showReasoning}
              >
                {showReasoning ? "Hide reasoning" : "Reasoning"}
              </button>
            )}
          </div>
          {msg.reasoning && showReasoning && (
            <div className="reasoning-content">
              <ReactMarkdown>{msg.reasoning}</ReactMarkdown>
            </div>
          )}
          <div className="agent-body">
            <div className="bubble">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
            {renderActivity(msg.blocks)}
          </div>
        </div>
      );
    }
    return (
      <div key={index} className="message error-message" role="alert">
        {msg.content}
      </div>
    );
  };

  return (
    <div
      className="app"
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {dragging && (
        <div className="drop-overlay" aria-hidden="true">
          <p>{isLoading ? "Wait for the agents to finish" : "Drop files to attach"}</p>
        </div>
      )}

      <main
        className={`stage show-${mobileView} ${workspaceOpen ? "workspace-open" : ""}`}
      >
        <DockLayout open={workspaceOpen}>
          <div className="main-col">
            <header className="topbar">
              <div className="brand">
                <AgentOrb state={orbState} />
                <div className="brand-text">
                  <h1>AgenticSeek</h1>
                  <span className={`status-line ${orbState}`}>{statusText}</span>
                </div>
              </div>
              <div className="topbar-actions">
                    <a
                      href="https://github.com/Fosowl/agenticSeek"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="icon-button ghost"
                      aria-label="View on GitHub"
                      title="GitHub"
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                      </svg>
                    </a>
                <button
                  type="button"
                  className="icon-button ghost"
                  onClick={() => setSettingsOpen(true)}
                  aria-label="Settings"
                  title="Settings"
                >
                  <Icon d={ICONS.settings} />
                </button>
                <ThemeToggle />
                <span className="topbar-divider" />
                <button
                  type="button"
                  className={`icon-button ghost workspace-toggle ${workspaceOpen ? "pressed" : ""}`}
                  onClick={() => setWorkspaceOpen((prev) => !prev)}
                  aria-pressed={workspaceOpen}
                  aria-label={workspaceOpen ? "Close workspace" : "Open workspace"}
                  title={workspaceOpen ? "Close workspace" : "Open workspace"}
                >
                  <Icon d={ICONS.panelRight} />
                </button>
              </div>
              <div className="segmented mobile-switch" role="tablist" aria-label="Pane">
                {[
                  ["chat", "Chat"],
                  ["workspace", "Workspace"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    role="tab"
                    aria-selected={mobileView === key}
                    className={mobileView === key ? "active" : ""}
                    onClick={() => setMobileView(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </header>
          <section className="chat-section" aria-label="Chat">
            <div className="messages">
              <div className="chat-column">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <img src={faviconPng} alt="AgenticSeek" className="empty-logo" />
                    <p className="eyebrow">Your local agents</p>
                    <h2>What should the agents do?</h2>
                    <p className="empty-sub">
                      They can browse the web, write and run code, and work with
                      files on your machine.
                    </p>
                    <div className="chips">
                      {SUGGESTIONS.map((text) => (
                        <button
                          key={text}
                          type="button"
                          className="chip"
                          onClick={() => pickSuggestion(text)}
                        >
                          {text}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map(renderMessage)
                )}
                {isLoading && (
                  <div className="thinking" aria-live="polite">
                    <span className="thinking-dots" aria-hidden="true">
                      <span />
                      <span />
                      <span />
                    </span>
                    <span className="shimmer">{status}</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
            <div className="chat-column composer-wrap">
              {!isOnline && (
                <p className="offline-note">
                  Backend offline. Start it first, or run <code>npm run mock</code>{" "}
                  for a fake one.
                </p>
              )}
              <form onSubmit={handleSubmit} className="composer">
                {attachments.length > 0 && (
                  <ul className="attachment-list">
                    {attachments.map((file, index) => (
                      <li key={`${file.name}-${index}`} className="attachment-chip">
                        <span className="attachment-name" title={file.name}>
                          {file.name}
                        </span>
                        <button
                          type="button"
                          onClick={() => removeAttachment(index)}
                          disabled={isLoading}
                          aria-label={`Remove ${file.name}`}
                        >
                          ×
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
                <textarea
                  ref={textareaRef}
                  rows={1}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={isLoading ? "Agents are working…" : "Ask anything…"}
                  aria-label="Message"
                  disabled={isLoading}
                />
                <div className="composer-actions">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    hidden
                    onChange={handleAttach}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading}
                    className="icon-button ghost"
                    aria-label="Attach files"
                    title="Attach files"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </button>
                  <span className="composer-hint">
                    {settings.sendWith === "ctrl-enter"
                      ? "Ctrl + Enter to send"
                      : "Shift + Enter for a new line"}
                  </span>
                  {isLoading ? (
                    <button
                      type="button"
                      onClick={handleStop}
                      className="send-button stop"
                      aria-label="Stop processing"
                      title="Stop"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24">
                        <rect x="5" y="5" width="14" height="14" rx="3" fill="currentColor" />
                      </svg>
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={!query.trim()}
                      className="send-button"
                      aria-label="Send message"
                      title="Send"
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M12 19V5M5 12l7-7 7 7"
                          stroke="currentColor"
                          strokeWidth="2.2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </form>
            </div>
          </section>
          </div>

          <section className="computer-section" aria-label="Workspace">
            <div className="panel-header">
              <div className="segmented" role="tablist" aria-label="Workspace view">
                {VIEWS.map(({ key, label }) => (
                  <button
                    key={key}
                    type="button"
                    role="tab"
                    aria-selected={currentView === key}
                    className={currentView === key ? "active" : ""}
                    onClick={() => setCurrentView(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className={`content ${currentView === "files" ? "content-files" : ""}`}>
              {error && <p className="error">{error}</p>}
              {currentView === "blocks" && (
                <div className="blocks">
                  {blockGroups.length > 0 ? (
                    blockGroups.map((group, index) => {
                      const last = group.runs[group.runs.length - 1];
                      return (
                        <div key={index} className="block">
                          <div className="block-header">
                            <span className="block-tool">{group.tool_type}</span>
                            {group.runs.length > 1 && (
                              <span className="runs-count">{group.runs.length} runs</span>
                            )}
                            <span className={`pill ${last.success ? "ok" : "fail"}`}>
                              {last.success ? "Success" : "Failure"}
                            </span>
                          </div>
                          <pre className="block-code">{group.block}</pre>
                          {last.feedback && <pre className="block-feedback">{last.feedback}</pre>}
                          {group.runs.length > 1 && (
                            <details className="block-runs">
                              <summary>Show all {group.runs.length} runs</summary>
                              {renderRuns(group.runs, "block-feedback")}
                            </details>
                          )}
                        </div>
                      );
                    })
                  ) : (
                    <div className="empty-pane">
                      <p className="eyebrow">Editor</p>
                      <p>Code and commands the agents run will show up here.</p>
                    </div>
                  )}
                </div>
              )}
              {currentView === "screenshot" &&
                (responseData?.screenshot ? (
                  <div className="browser-frame">
                    <div className="browser-bar">
                      <span />
                      <span />
                      <span />
                      <p className="eyebrow">Live view</p>
                    </div>
                    <img src={responseData.screenshot} alt="What the browser agent sees" />
                  </div>
                ) : (
                  <div className="empty-pane">
                    <p className="eyebrow">Browser</p>
                    <p>When an agent browses the web, its screen appears here.</p>
                  </div>
                ))}
              {/* Kept mounted so the expanded tree and open file survive tab switches. */}
              <div hidden={currentView !== "files"} className="files-pane">
                <FileExplorer
                  backendUrl={BACKEND_URL}
                  active={currentView === "files" && workspaceVisible && !authRequired}
                />
              </div>
            </div>
          </section>
        </DockLayout>
      </main>
      <SettingsDialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        backendUrl={BACKEND_URL}
        isOnline={isOnline}
        hasToken={Boolean(getToken())}
        onChangeToken={changeTokenFromSettings}
        onClearToken={clearTokenFromSettings}
      />
      {tokenPrompt && (
        <TokenPrompt
          reason={tokenPrompt}
          hasToken={Boolean(getToken())}
          onSave={handleSaveToken}
          onClear={handleClearToken}
          onCancel={() => setTokenPrompt(null)}
        />
      )}
    </div>
  );
}

export default App;
