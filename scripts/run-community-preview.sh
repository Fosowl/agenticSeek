#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/agentic-seek-front"
STATE_DIR="$ROOT_DIR/.community-preview"
VENV_DIR="$ROOT_DIR/.venv-community"
BACKEND_PORT="${BACKEND_PORT:-7777}"
FRONTEND_PORT="${FRONTEND_PORT:-4310}"

mkdir -p "$STATE_DIR"

BACKEND_PID_FILE="$STATE_DIR/backend.pid"
FRONTEND_PID_FILE="$STATE_DIR/frontend.pid"
BACKEND_LOG="$STATE_DIR/backend.log"
FRONTEND_LOG="$STATE_DIR/frontend.log"

is_port_open() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn | awk '{print $4}' | grep -q ":${port}$"
  else
    netstat -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${port}$"
  fi
}

start_backend() {
  if is_port_open "$BACKEND_PORT"; then
    echo "Backend already listening on :$BACKEND_PORT"
    return
  fi

  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating lightweight venv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  pip install --disable-pip-version-check --no-cache-dir -r "$ROOT_DIR/requirements.community.txt" >/dev/null

  echo "Starting community backend on :$BACKEND_PORT"
  nohup "$VENV_DIR/bin/uvicorn" community_api:api \
    --app-dir "$ROOT_DIR" \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
    >"$BACKEND_LOG" 2>&1 &

  echo $! >"$BACKEND_PID_FILE"
}

start_frontend() {
  if is_port_open "$FRONTEND_PORT"; then
    echo "Frontend already listening on :$FRONTEND_PORT"
    return
  fi

  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    echo "Installing frontend dependencies"
    (cd "$FRONTEND_DIR" && npm install --no-audit --no-fund >/dev/null)
  fi

  echo "Starting frontend on :$FRONTEND_PORT"
  nohup env \
    PORT="$FRONTEND_PORT" \
    BROWSER=none \
    REACT_APP_BACKEND_URL="http://localhost:$BACKEND_PORT" \
    npm --prefix "$FRONTEND_DIR" start \
    >"$FRONTEND_LOG" 2>&1 &

  echo $! >"$FRONTEND_PID_FILE"
}

wait_for_health() {
  echo "Waiting for backend health endpoint"
  for _ in {1..30}; do
    if curl -s "http://localhost:${BACKEND_PORT}/health" >/dev/null 2>&1; then
      echo "Backend is healthy"
      return
    fi
    sleep 1
  done
  echo "Backend did not become healthy. Check $BACKEND_LOG"
  exit 1
}

start_backend
wait_for_health
start_frontend

echo ""
echo "Community preview is running:"
echo "- Frontend: http://localhost:${FRONTEND_PORT}"
echo "- Backend:  http://localhost:${BACKEND_PORT}"
echo ""
echo "Logs:"
echo "- $BACKEND_LOG"
echo "- $FRONTEND_LOG"
echo ""
echo "Stop with: $ROOT_DIR/scripts/stop-community-preview.sh"
