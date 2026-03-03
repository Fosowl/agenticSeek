#!/bin/bash

source .env

command_exists() {
    command -v "$1" &> /dev/null
}
if [ -z "$WORK_DIR" ]; then
    echo "Error: WORK_DIR environment variable is not set. Please set it in your .env file."
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    dir_size_bytes=$(du -s -b "$WORK_DIR" 2>/dev/null | awk '{print $1}')
else
    dir_size_bytes=$(du -s --bytes "$WORK_DIR" 2>/dev/null | awk '{print $1}')
fi

max_size_bytes=$((2 * 1024 * 1024 * 1024 * 10))

echo "Mounting $WORK_DIR ($dir_size_bytes bytes) to docker."

if [ "$dir_size_bytes" -gt "$max_size_bytes" ]; then
    echo "Error: WORK_DIR ($WORK_DIR) contains more than 20GB of data ($(du -sh "$WORK_DIR" 2>/dev/null | awk '{print $1}'))."
    exit 1
fi

if [ "$1" = "full" ]; then
    echo "Starting full deployment with backend and all services..."
else
    echo "Starting core deployment with frontend and search services only... use ./start_services.sh full to start backend as well"
fi

if ! command_exists docker; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "On Ubuntu: sudo apt install docker.io"
    echo "On macOS/Windows: Install Docker Desktop from https://www.docker.com/get-started/"
    exit 1
fi

# Check if Docker daemon is running
echo "Checking if Docker daemon is running..."
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running or inaccessible."
    if [ "$(uname)" = "Linux" ]; then
        echo "Trying to start Docker service (may require sudo)..."
        if sudo systemctl start docker &> /dev/null; then
            echo "Docker started successfully."
        else
            echo "Failed to start Docker. Possible issues:"
            echo "1. Run this script with sudo: sudo bash setup_searxng.sh"
            echo "2. Check Docker installation: sudo systemctl status docker"
            echo "3. Add your user to the docker group: sudo usermod -aG docker $USER (then log out and back in)"
            exit 1
        fi
    else
        echo "Please start Docker manually:"
        echo "- On macOS/Windows: Open Docker Desktop."
        echo "- On Linux: Run 'sudo systemctl start docker' or check your distro's docs."
        exit 1
    fi
else
    echo "Docker daemon is running."
fi

# Check if Docker Compose is installed
# Prefer the newer 'docker compose' command if available
if docker compose version >/dev/null 2>&1; then
    echo "Using newer docker compose (v2)."
    COMPOSE_CMD="docker compose"
elif command_exists docker-compose; then
    echo "Using old docker-compose."
    COMPOSE_CMD="docker-compose"
else
    echo "Error: Docker Compose is not installed. Please install it first."
    echo "On Ubuntu: sudo apt install docker-compose-plugin"
    echo "Or install Docker Desktop which includes compose v2"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found in the current directory."
    exit 1
fi

# Stop only the backend container if it's running to ensure a clean state
if docker ps --format '{{.Names}}' | grep -q '^backend$'; then
    echo "New start: (re)starting backend container..."
    docker stop backend
    echo "Backend container stopped."
fi

# export searxng secret key (cross-platform)
if command -v openssl &> /dev/null; then
    export SEARXNG_SECRET_KEY=$(openssl rand -hex 32)
else
    # Fallback: use Python if openssl is not available
    if command -v python3 &> /dev/null; then
        export SEARXNG_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    else
        echo "Error: Neither openssl nor python is available to generate a secret key."
        exit 1
    fi
fi

if [ "$1" = "full" ]; then
    # First start backend and wait for it to be healthy
    echo "Full docker deployment. Starting backend service..."
    if ! $COMPOSE_CMD up -d backend; then
        echo "Error: Failed to start backend container."
        exit 1
    fi
    # Wait for backend to be healthy (check if it's running and not restarting)
    echo "Waiting for backend to be ready..."
    for i in {1..30}; do
        if [ "$(docker inspect -f '{{.State.Running}}' backend)" = "true" ] && \
           [ "$(docker inspect -f '{{.State.Restarting}}' backend)" = "false" ]; then
            echo "backend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "Error: backend failed to start properly after 30 seconds"
            $COMPOSE_CMD logs backend 
            exit 1
        fi
        sleep 1
    done
    if ! $COMPOSE_CMD --profile full up; then
        echo "Error: Failed to start containers. Check Docker logs with '$COMPOSE_CMD logs'."
        echo "Possible fixes: Run with sudo or ensure port 8080 is free."
        exit 1
    fi
else
    if ! $COMPOSE_CMD --profile core up; then
        echo "Error: Failed to start containers. Check Docker logs with '$COMPOSE_CMD logs'."
        echo "Possible fixes: Run with sudo or ensure port 8080 is free."
        exit 1
    fi
fi
sleep 10
