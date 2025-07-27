#!/bin/bash

SCRIPTS_DIR="scripts"
LLM_ROUTER_DIR="llm_router"
IS_LOCAL=$(grep "^is_local" config.ini | cut -d'=' -f2 | xargs)
PROVIDER=$(grep "^provider_name" config.ini | cut -d'=' -f2 | xargs)
MODEL=$(grep "^provider_model" config.ini | cut -d'=' -f2 | xargs)


echo "Detecting operating system..."

OS_TYPE=$(uname -s)


case "$OS_TYPE" in
    "Linux"*)
        echo "Detected Linux OS"
        if [ -f "$SCRIPTS_DIR/linux_install.sh" ]; then
            echo "Running Linux installation script..."
            bash "$SCRIPTS_DIR/linux_install.sh"
            bash -c "cd $LLM_ROUTER_DIR && ./dl_safetensors.sh"
        else
            echo "Error: $SCRIPTS_DIR/linux_install.sh not found!"
            exit 1
        fi
	if [ "$IS_LOCAL" = "True" ] && [ "$PROVIDER" = "ollama" ]; then
	    echo "Create ollama image with $MODEL model"
	    bash "$SCRIPTS_DIR/ollama_install.sh" "$MODEL"
	fi
        ;;
    "Darwin"*)
        echo "Detected macOS"
        if [ -f "$SCRIPTS_DIR/macos_install.sh" ]; then
            echo "Running macOS installation script..."
            bash "$SCRIPTS_DIR/macos_install.sh"
            bash -c "cd $LLM_ROUTER_DIR && ./dl_safetensors.sh"
        else
            echo "Error: $SCRIPTS_DIR/macos_install.sh not found!"
            exit 1
        fi
        ;;
    *)
        echo "Unsupported OS detected: $OS_TYPE"
        echo "This script supports only Linux and macOS."
        exit 1
        ;;
esac

echo "Installation process finished!"
