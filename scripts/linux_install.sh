#!/usr/bin/env bash

echo "Starting installation for Linux..."

set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "You can install it using: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Update package list
sudo apt-get update || { echo "Failed to update package list"; exit 1; }
# make sure essential tool are installed
sudo apt-get install -y \
    python3-dev \
    build-essential \
    alsa-utils \
    portaudio19-dev \
    python3-pyaudio \
    libgtk-3-dev \
    libnotify-dev \
    libgconf-2-4 \
    libnss3 \
    libxss1 || { echo "Failed to install packages"; exit 1; }

# Initialize uv project if pyproject.toml doesn't exist
if [ ! -f "pyproject.toml" ]; then
    echo "Initializing uv project..."
    uv init --python 3.10 || { echo "Failed to initialize uv project"; exit 1; }
fi

# Sync the project (creates venv and installs dependencies)
echo "Setting up Python environment with uv..."
uv sync --python 3.10 || { echo "Failed to sync uv project"; exit 1; }

# Add specific packages
echo "Adding Selenium..."
uv add selenium || { echo "Failed to add selenium"; exit 1; }

# Add dependencies from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "Adding dependencies from requirements.txt..."
    uv add -r requirements.txt || { echo "Failed to add requirements from requirements.txt"; exit 1; }
fi

# install docker compose
sudo apt install -y docker-compose

echo "Installation complete for Linux!"
echo "To activate the environment, run: source .venv/bin/activate"
echo "Or run commands with: uv run <command>"