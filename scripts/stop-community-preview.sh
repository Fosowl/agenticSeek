#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$ROOT_DIR/.community-preview"

stop_pid_file() {
  local name="$1"
  local pid_file="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "$name pid file not found, skipping"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    echo "Stopped $name (pid $pid)"
  else
    echo "$name process not running"
  fi

  rm -f "$pid_file"
}

stop_pid_file "backend" "$STATE_DIR/backend.pid"
stop_pid_file "frontend" "$STATE_DIR/frontend.pid"

echo "Community preview stop routine finished"
