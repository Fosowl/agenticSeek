import React, { useState, useEffect, useRef, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import "./App.css";
import { ThemeToggle } from "./components/ThemeToggle";
import { ResizableLayout } from "./components/ResizableLayout";
import { FileExplorer } from "./components/FileExplorer";
import { TokenPrompt } from "./components/TokenPrompt";
import { clearToken, getToken, onAuthRequired, saveToken } from "./apiAuth";
import faviconPng from "./logo.png";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
console.log("Using backend URL:", BACKEND_URL);

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState("blocks");
  const [responseData, setResponseData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [status, setStatus] = useState("Agents ready");
  const [expandedReasoning, setExpandedReasoning] = useState(new Set());
  // null, or why the token prompt is open: "required", "rejected", "change".
  const [tokenPrompt, setTokenPrompt] = useState(null);
  // Files picked with the paperclip, uploaded when the query is sent.
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  const authRequired = tokenPrompt === "required" || tokenPrompt === "rejected";
  const messagesEndRef = useRef(null);
  // Normalized texts of agent answers already shown. A ref (not `messages`)
  // because polls overlap when the backend is slow: every in-flight response
  // must see answers appended by responses that resolved before it.
  const seenAnswersRef = useRef(new Set());

  const fetchLatestAnswer = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/latest_answer`);
      const data = res.data;

      updateData(data);
      if (!data.answer || data.answer.trim() === "") {
        return;
      }
      const normalizedNewAnswer = normalizeAnswer(data.answer);
      if (seenAnswersRef.current.has(normalizedNewAnswer)) {
        return;
      }
      seenAnswersRef.current.add(normalizedNewAnswer);
      setMessages((prev) => [
        ...prev,
        {
          type: "agent",
          content: data.answer,
          reasoning: data.reasoning,
          agentName: data.agent_name,
          status: data.status,
          uid: data.uid,
        },
      ]);
      setStatus(data.status);
      scrollToBottom();
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
      const timestamp = new Date().getTime();
      const res = await axios.get(`${BACKEND_URL}/screenshot`, {
        params: { timestamp },
        responseType: "blob",
      });
      console.log("Screenshot fetched successfully");
      const imageUrl = URL.createObjectURL(res.data);
      setResponseData((prev) => {
        if (prev?.screenshot && prev.screenshot !== "placeholder.png") {
          URL.revokeObjectURL(prev.screenshot);
        }
        return {
          ...prev,
          screenshot: imageUrl,
          screenshotTimestamp: new Date().getTime(),
        };
      });
    } catch (err) {
      console.error("Error fetching screenshot:", err);
      setResponseData((prev) => ({
        ...prev,
        screenshot: "placeholder.png",
        screenshotTimestamp: new Date().getTime(),
      }));
    }
  };

  const normalizeAnswer = (answer) => {
    return answer
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ")
      .replace(/[.,!?]/g, "");
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
      blocks: data.blocks || prev.blocks || null,
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
    setIsLoading(false);
    setError(null);
    try {
      await axios.get(`${BACKEND_URL}/stop`);
      setStatus("Requesting stop...");
    } catch (err) {
      console.error("Error stopping the agent:", err);
    }
  };

  const handleAttach = (e) => {
    const picked = Array.from(e.target.files || []);
    setAttachments((prev) => [...prev, ...picked]);
    // Reset so picking the same file again fires onChange.
    e.target.value = "";
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
    if (!query.trim()) {
      console.log("Empty query");
      return;
    }
    setIsLoading(true);
    setError(null);
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
      setQuery("waiting for response...");
      const res = await axios.post(`${BACKEND_URL}/query`, {
        query: fullQuery,
        tts_enabled: false,
      });
      setQuery("Enter your query...");
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

  const handleGetScreenshot = async () => {
    try {
      setCurrentView("screenshot");
    } catch (err) {
      setError("Browser not in use");
    }
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

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="logo-container">
            <img src={faviconPng} alt="AgenticSeek" className="logo-icon" />
          </div>
          <div className="brand-text">
            <h1>AgenticSeek</h1>
          </div>
        </div>
        <div className="header-status">
          <div
            className={`status-indicator ${isOnline ? "online" : "offline"}`}
          >
            <div className="status-dot"></div>
            <span className="status-text">
              {isOnline ? "Online" : "Offline"}
            </span>
          </div>
        </div>
        <div className="header-actions">
          <a
            href="https://github.com/Fosowl/agenticSeek"
            target="_blank"
            rel="noopener noreferrer"
            className="action-button github-link"
            aria-label="View on GitHub"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            <span className="action-text">GitHub</span>
          </a>
          <button
            type="button"
            className="action-button"
            onClick={() => setTokenPrompt("change")}
            aria-label="Change API token"
            title="Change API token"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M15 7a4 4 0 1 1-3.87 5H9v2H7v2H4v-3l5.13-5.13A4 4 0 0 1 15 7z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="action-text">Token</span>
          </button>
          <div>
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="main">
        <ResizableLayout initialLeftWidth={50}>
          <div className="chat-section">
            <h2>Chat Interface</h2>
            <div className="messages">
              {messages.length === 0 ? (
                <p className="placeholder">
                  No messages yet. Type below to start!
                </p>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message ${
                      msg.type === "user"
                        ? "user-message"
                        : msg.type === "agent"
                        ? "agent-message"
                        : "error-message"
                    }`}
                  >
                    <div className="message-header">
                      {msg.type === "agent" && (
                        <span className="agent-name">{msg.agentName}</span>
                      )}
                      {msg.type === "agent" &&
                        msg.reasoning &&
                        expandedReasoning.has(index) && (
                          <div className="reasoning-content">
                            <ReactMarkdown>{msg.reasoning}</ReactMarkdown>
                          </div>
                        )}
                      {msg.type === "agent" && (
                        <button
                          className="reasoning-toggle"
                          onClick={() => toggleReasoning(index)}
                          title={
                            expandedReasoning.has(index)
                              ? "Hide reasoning"
                              : "Show reasoning"
                          }
                        >
                          {expandedReasoning.has(index) ? "▼" : "▶"} Reasoning
                        </button>
                      )}
                    </div>
                    <div className="message-content">
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
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
            {isOnline && <div className="loading-animation">{status}</div>}
            {!isLoading && !isOnline && (
              <p className="loading-animation">
                System offline. Deploy backend first.
              </p>
            )}
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
            <form onSubmit={handleSubmit} className="input-form">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your query..."
                disabled={isLoading}
              />
              <div className="action-buttons">
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
                  className="icon-button attach-button"
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
                <button
                  type="submit"
                  disabled={isLoading}
                  className="icon-button"
                  aria-label="Send message"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
                <button
                  type="button"
                  onClick={handleStop}
                  className="icon-button stop-button"
                  aria-label="Stop processing"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <rect
                      x="6"
                      y="6"
                      width="12"
                      height="12"
                      fill="currentColor"
                      rx="2"
                    />
                  </svg>
                </button>
              </div>
            </form>
          </div>

          <div className="computer-section">
            <h2>Computer View</h2>
            <div className="view-selector">
              <button
                className={currentView === "blocks" ? "active" : ""}
                onClick={() => setCurrentView("blocks")}
              >
                Editor View
              </button>
              <button
                className={currentView === "screenshot" ? "active" : ""}
                onClick={
                  responseData?.screenshot
                    ? () => setCurrentView("screenshot")
                    : handleGetScreenshot
                }
              >
                Browser View
              </button>
              <button
                className={currentView === "files" ? "active" : ""}
                onClick={() => setCurrentView("files")}
              >
                Files
              </button>
            </div>
            <div className={`content ${currentView === "files" ? "content-files" : ""}`}>
              {error && <p className="error">{error}</p>}
              {currentView === "blocks" && (
                <div className="blocks">
                  {responseData &&
                  responseData.blocks &&
                  Object.values(responseData.blocks).length > 0 ? (
                    Object.values(responseData.blocks).map((block, index) => (
                      <div key={index} className="block">
                        <p className="block-tool">Tool: {block.tool_type}</p>
                        <pre>{block.block}</pre>
                        <p className="block-feedback">
                          Feedback: {block.feedback}
                        </p>
                        {block.success ? (
                          <p className="block-success">Success</p>
                        ) : (
                          <p className="block-failure">Failure</p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="block">
                      <p className="block-tool">Tool: No tool in use</p>
                      <pre>No file opened</pre>
                    </div>
                  )}
                </div>
              )}
              {currentView === "screenshot" && (
                <div className="screenshot">
                  <img
                    src={responseData?.screenshot || "placeholder.png"}
                    alt="Screenshot"
                    onError={(e) => {
                      e.target.src = "placeholder.png";
                      console.error("Failed to load screenshot");
                    }}
                    key={responseData?.screenshotTimestamp || "default"}
                  />
                </div>
              )}
              {/* Kept mounted so the expanded tree and open file survive tab switches. */}
              <div hidden={currentView !== "files"} className="files-pane">
                <FileExplorer
                  backendUrl={BACKEND_URL}
                  active={currentView === "files" && !authRequired}
                />
              </div>
            </div>
          </div>
        </ResizableLayout>
      </main>
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
