import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "./FileExplorer.css";

const ROOT = "";
const MARKDOWN_FILE = /\.(md|markdown)$/i;

const formatBytes = (bytes) => {
  if (bytes == null) return "";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${unit === 0 ? value : value.toFixed(1)} ${units[unit]}`;
};

const errorMessage = (err) =>
  err.response?.data?.detail || err.message || "Request failed";

const indent = (depth) => ({ paddingLeft: `${0.5 + depth * 1}rem` });

export const FileExplorer = ({ backendUrl, active }) => {
  // directory path -> { entries, loading, error }
  const [directories, setDirectories] = useState({});
  const [expanded, setExpanded] = useState(() => new Set());
  const [selectedPath, setSelectedPath] = useState(null);
  // { meta, imageUrl, loading, error } for the selected file
  const [file, setFile] = useState(null);
  const [showSource, setShowSource] = useState(false);
  const fileRequestId = useRef(0);
  const stateRef = useRef({ expanded, selectedPath });

  useEffect(() => {
    stateRef.current = { expanded, selectedPath };
  });

  const imageUrl = file?.imageUrl;
  useEffect(
    () => () => {
      if (imageUrl) URL.revokeObjectURL(imageUrl);
    },
    [imageUrl]
  );

  const loadDirectory = useCallback(
    async (path) => {
      setDirectories((prev) => ({
        ...prev,
        [path]: { entries: prev[path]?.entries || [], loading: true, error: null },
      }));
      try {
        const res = await axios.get(`${backendUrl}/files/list`, {
          params: { path },
        });
        setDirectories((prev) => ({
          ...prev,
          [path]: { entries: res.data.entries, loading: false, error: null },
        }));
      } catch (err) {
        setDirectories((prev) => ({
          ...prev,
          [path]: { entries: [], loading: false, error: errorMessage(err) },
        }));
      }
    },
    [backendUrl]
  );

  const openFile = useCallback(
    async (path) => {
      const requestId = ++fileRequestId.current;
      setSelectedPath(path);
      setFile((prev) =>
        prev?.meta?.path === path ? { ...prev, loading: true } : { loading: true }
      );
      try {
        const { data: meta } = await axios.get(`${backendUrl}/files/content`, {
          params: { path },
        });
        let url = null;
        if (meta.kind === "image") {
          const res = await axios.get(`${backendUrl}/files/raw`, {
            params: { path, t: Date.now() },
            responseType: "blob",
          });
          url = URL.createObjectURL(res.data);
        }
        if (requestId !== fileRequestId.current) {
          if (url) URL.revokeObjectURL(url);
          return;
        }
        setFile({ meta, imageUrl: url, loading: false, error: null });
      } catch (err) {
        if (requestId !== fileRequestId.current) return;
        setFile({ meta: null, imageUrl: null, loading: false, error: errorMessage(err) });
      }
    },
    [backendUrl]
  );

  const refresh = useCallback(() => {
    const { expanded: open, selectedPath: selected } = stateRef.current;
    loadDirectory(ROOT);
    open.forEach((path) => loadDirectory(path));
    if (selected) openFile(selected);
  }, [loadDirectory, openFile]);

  useEffect(() => {
    if (active) refresh();
  }, [active, refresh]);

  const toggleDirectory = (path) => {
    const willOpen = !expanded.has(path);
    setExpanded((prev) => {
      const next = new Set(prev);
      if (willOpen) next.add(path);
      else next.delete(path);
      return next;
    });
    if (willOpen) loadDirectory(path);
  };

  const renderDirectory = (path, depth) => {
    const directory = directories[path];
    if (!directory) return null;
    if (directory.error) {
      return (
        <div className="file-tree-message file-tree-error" style={indent(depth)}>
          {directory.error}
        </div>
      );
    }
    if (directory.entries.length === 0) {
      return directory.loading ? null : (
        <div className="file-tree-message" style={indent(depth)}>
          {path === ROOT ? "Workspace is empty" : "Empty folder"}
        </div>
      );
    }
    return directory.entries.map((entry) => {
      if (entry.type === "directory") {
        const isOpen = expanded.has(entry.path);
        return (
          <React.Fragment key={entry.path}>
            <button
              type="button"
              className="file-tree-item"
              style={indent(depth)}
              onClick={() => toggleDirectory(entry.path)}
              title={entry.path}
            >
              <span className="file-tree-caret">{isOpen ? "▾" : "▸"}</span>
              <span className="file-tree-icon">{isOpen ? "📂" : "📁"}</span>
              <span className="file-tree-name">{entry.name}</span>
            </button>
            {isOpen && renderDirectory(entry.path, depth + 1)}
          </React.Fragment>
        );
      }
      return (
        <button
          type="button"
          key={entry.path}
          className={`file-tree-item ${selectedPath === entry.path ? "selected" : ""}`}
          style={indent(depth)}
          onClick={() => openFile(entry.path)}
          title={entry.path}
        >
          <span className="file-tree-caret" />
          <span className="file-tree-icon">📄</span>
          <span className="file-tree-name">{entry.name}</span>
          <span className="file-tree-size">{formatBytes(entry.size)}</span>
        </button>
      );
    });
  };

  const renderFileBody = (meta) => {
    if (meta.kind === "image") {
      return (
        <div className="file-image">
          {file.imageUrl && <img src={file.imageUrl} alt={meta.name} />}
        </div>
      );
    }
    if (meta.kind === "binary") {
      return <p className="placeholder">Binary file — preview not available.</p>;
    }
    if (MARKDOWN_FILE.test(meta.name) && !showSource) {
      return (
        <div className="file-markdown">
          <ReactMarkdown>{meta.content}</ReactMarkdown>
        </div>
      );
    }
    return <pre className="file-text">{meta.content}</pre>;
  };

  const renderViewer = () => {
    if (!selectedPath) {
      return <p className="placeholder">Select a file to view its content.</p>;
    }
    if (file?.error) {
      return <p className="error">{file.error}</p>;
    }
    if (!file?.meta) {
      return <p className="placeholder">Loading…</p>;
    }
    const { meta } = file;
    return (
      <>
        <div className="file-viewer-header">
          <span className="file-viewer-path" title={meta.path}>
            {meta.path}
          </span>
          <span className="file-viewer-size">{formatBytes(meta.size)}</span>
          {meta.kind === "text" && MARKDOWN_FILE.test(meta.name) && (
            <button
              type="button"
              className="file-explorer-button"
              onClick={() => setShowSource((prev) => !prev)}
            >
              {showSource ? "Preview" : "Source"}
            </button>
          )}
        </div>
        {meta.truncated && (
          <p className="file-viewer-note">
            File too large: showing only the beginning ({formatBytes(meta.size)}{" "}
            total).
          </p>
        )}
        <div className="file-viewer-body">{renderFileBody(meta)}</div>
      </>
    );
  };

  return (
    <div className="file-explorer">
      <div className="file-tree">
        <div className="file-tree-toolbar">
          <span>Workspace</span>
          <button
            type="button"
            className="file-explorer-button"
            onClick={refresh}
            title="Reload the file tree and the open file"
          >
            ⟳ Refresh
          </button>
        </div>
        <div className="file-tree-entries">{renderDirectory(ROOT, 0)}</div>
      </div>
      <div className="file-viewer">{renderViewer()}</div>
    </div>
  );
};
