#!/bin/sh
# AgenticSeek backend container entrypoint.
# Starts Xvfb so Chrome can run headed inside Docker (headless mode leaks
# detection tells; a real window under Xvfb does not), then runs the backend.
set -e

if command -v Xvfb >/dev/null 2>&1; then
    if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
        echo "Starting Xvfb on $DISPLAY (1920x1080x24)"
        Xvfb "$DISPLAY" -screen 0 1920x1080x24 -nolisten tcp &
        sleep 1
    fi
else
    echo "Xvfb not found: falling back to headless (AGENTICSEEK_HEADLESS=1)"
    export AGENTICSEEK_HEADLESS=1
fi

exec "$@"
