import React, { useState } from "react";

// reason: "required" (no token saved), "rejected" (saved token refused),
// or "change" (opened by the user; can be cancelled).
export const TokenPrompt = ({ reason, hasToken, onSave, onClear, onCancel }) => {
  const [value, setValue] = useState("");
  const canCancel = reason === "change";

  const handleSubmit = (e) => {
    e.preventDefault();
    const token = value.trim();
    if (token) onSave(token);
  };

  return (
    <div className="token-overlay">
      <form
        className="token-dialog"
        onSubmit={handleSubmit}
        role="dialog"
        aria-modal="true"
        aria-labelledby="token-title"
      >
        <h2 id="token-title">
          {canCancel ? "Change API token" : "API token required"}
        </h2>
        <p>
          The AgenticSeek backend only answers requests that carry its API
          token. The token is saved in this browser only.
        </p>
        {reason === "rejected" && (
          <p className="token-error" role="alert">
            The backend rejected the saved token. Check it and try again.
          </p>
        )}
        <p>Where to find it:</p>
        <ul className="token-help">
          <li>
            Docker: <code>docker compose logs backend | grep "API token"</code>{" "}
            or <code>docker exec backend cat /opt/agent-runtime/api_token</code>
          </li>
          <li>
            Host: the line starting with <code>AgenticSeek API token:</code>{" "}
            printed by <code>python api.py</code>
          </li>
        </ul>
        <input
          type="password"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Paste the API token"
          aria-label="API token"
          autoComplete="off"
          autoFocus
        />
        <div className="token-actions">
          {canCancel && hasToken && (
            <button type="button" className="token-secondary" onClick={onClear}>
              Clear saved token
            </button>
          )}
          {canCancel && (
            <button type="button" className="token-secondary" onClick={onCancel}>
              Cancel
            </button>
          )}
          <button type="submit" className="token-primary" disabled={!value.trim()}>
            Save
          </button>
        </div>
      </form>
    </div>
  );
};
