#!/bin/bash

set -euo pipefail

# Script to start services with Docker Compose
# Usage: ./start_services.sh [full]

# Change to the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Please copy .env.example to .env and configure it."
fi

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Get WORK_DIR from environment or use default
WORK_DIR="${WORK_DIR:-/tmp/agentic_seek_workspace}"
mkdir -p "$WORK_DIR"

echo "Mounting $WORK_DIR to docker."

# Default profile is "core" unless "full" is specified
PROFILE="${1:-core}"
if [ "$PROFILE" = "full" ]; then
    PROFILE="full"
    echo "Starting full deployment with frontend, search, and backend services..."
else
    PROFILE="core"
    echo "Starting core deployment with frontend and search services only... use ./start_services.sh full to start backend as well"
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

echo "Docker daemon is running."

# Check if we have newer docker compose (v2)
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
    echo "Using newer docker compose (v2)."
else
    DOCKER_COMPOSE="docker-compose"
    echo "Using older docker compose (v1)."
fi

# Build and start services
echo "Building and starting services with profile: $PROFILE"

# First, build all services to ensure dependencies are installed
$DOCKER_COMPOSE build --no-cache

# Then start the services with the specified profile
$DOCKER_COMPOSE --profile "$PROFILE" up --detach

echo "Services started successfully!"
echo "Frontend available at: http://localhost:3000"
if [ "$PROFILE" = "full" ]; then
    echo "Backend API available at: http://localhost:7777"
fi
echo "SearXNG available at: http://localhost:8080"

# Show logs
echo "Showing logs (press Ctrl+C to stop following):"
$DOCKER_COMPOSE --profile "$PROFILE" logs -f