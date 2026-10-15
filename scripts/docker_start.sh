#!/bin/sh
# AgenticSeek backend container entrypoint.
# Starts Xvfb so Chrome can run headed inside Docker (headless mode leaks
# detection tells; a real window under Xvfb does not), prepares the
# unprivileged sandbox for agent-run code, then runs the backend.
set -e

RUNTIME_DIR="${AGENT_RUNTIME_DIR:-/opt/agent-runtime}"
BROWSER_PROFILE_DIR="$PWD/.browser_profile"
DOCKER_DNS_IP="127.0.0.11"

# Run agent code as AGENTICSEEK_EXEC_UID: align the 'agent' user with it.
align_agent_user() {
    exec_gid="${AGENTICSEEK_EXEC_GID:-$AGENTICSEEK_EXEC_UID}"
    if [ "$(id -g agent)" != "$exec_gid" ]; then
        groupmod -o -g "$exec_gid" agent
    fi
    if [ "$(id -u agent)" != "$AGENTICSEEK_EXEC_UID" ]; then
        usermod -o -u "$AGENTICSEEK_EXEC_UID" agent
    fi
    chown -R "$AGENTICSEEK_EXEC_UID:$exec_gid" /home/agent
}

# Sessions, logs, API token and browser profile stay root-only.
lock_private_dirs() {
    mkdir -p "$RUNTIME_DIR" "$BROWSER_PROFILE_DIR"
    chmod 700 "$RUNTIME_DIR" "$BROWSER_PROFILE_DIR"
}

# chromedriver and Chrome DevTools listen on loopback without auth and run as
# root: block loopback for the agent uid, except Docker's embedded DNS.
block_agent_loopback() {
    owner="-o lo -m owner --uid-owner $AGENTICSEEK_EXEC_UID"
    iptables -C OUTPUT $owner -d "$DOCKER_DNS_IP" -j ACCEPT 2>/dev/null \
        || iptables -A OUTPUT $owner -d "$DOCKER_DNS_IP" -j ACCEPT || return 1
    iptables -C OUTPUT $owner -j REJECT 2>/dev/null \
        || iptables -A OUTPUT $owner -j REJECT || return 1
    ip6tables -C OUTPUT $owner -j REJECT 2>/dev/null \
        || ip6tables -A OUTPUT $owner -j REJECT 2>/dev/null || true
}

setup_exec_sandbox() {
    if [ -z "${AGENTICSEEK_EXEC_UID:-}" ] || [ "$AGENTICSEEK_EXEC_UID" = "0" ]; then
        echo "WARNING: AGENTICSEEK_EXEC_UID unset or 0: agent code runs as root."
        return
    fi
    case "$AGENTICSEEK_EXEC_UID${AGENTICSEEK_EXEC_GID:-}" in
        *[!0-9]*)
            echo "ERROR: AGENTICSEEK_EXEC_UID/AGENTICSEEK_EXEC_GID must be numeric ids."
            exit 1 ;;
    esac
    align_agent_user
    lock_private_dirs
    if block_agent_loopback; then
        echo "Agent code runs as uid $AGENTICSEEK_EXEC_UID with loopback blocked."
    else
        echo "WARNING: could not block loopback for agent code (needs cap NET_ADMIN)."
        echo "WARNING: agent code can reach chromedriver/DevTools and regain root."
    fi
}

start_xvfb() {
    if ! command -v Xvfb >/dev/null 2>&1; then
        echo "Xvfb not found: falling back to headless (AGENTICSEEK_HEADLESS=1)"
        export AGENTICSEEK_HEADLESS=1
        return
    fi
    if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
        # No server answers on $DISPLAY, so any lock/socket is stale: docker
        # stop SIGKILLs Xvfb and leaves them in the container layer. After a
        # restart the lock's PID is recycled by a live process and Xvfb aborts
        # with "Server is already active for display".
        display_num="${DISPLAY#:}"
        display_num="${display_num%%.*}"
        rm -f "/tmp/.X${display_num}-lock" "/tmp/.X11-unix/X${display_num}"
        echo "Starting Xvfb on $DISPLAY (1920x1080x24)"
        # No TCP and no abstract socket: only the root-only path socket below.
        Xvfb "$DISPLAY" -screen 0 1920x1080x24 -nolisten tcp -nolisten local &
        sleep 1
        if [ -d /tmp/.X11-unix ]; then chmod 700 /tmp/.X11-unix; fi
    fi
}

setup_exec_sandbox
start_xvfb
exec "$@"
