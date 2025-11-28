#!/usr/bin/env bash

echo "Starting installation for macOS..."

set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "You can install it using: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# update
brew update
# make sure wget installed
brew install wget
# Install chromedriver using Homebrew
brew install --cask chromedriver
# Install portaudio for pyAudio using Homebrew
brew install portaudio

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

echo "Installation complete for macOS!"
echo "To activate the environment, run: source .venv/bin/activate"
echo "Or run commands with: uv run <command>"