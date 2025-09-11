#!/bin/bash

SCRIPTS_DIR="scripts"
LLM_ROUTER_DIR="llm_router"

echo "Running Linux installation script..."

if [ -f "$SCRIPTS_DIR/linux_install.sh" ]; then
    bash "$SCRIPTS_DIR/linux_install.sh"
    bash -c "cd $LLM_ROUTER_DIR && ./dl_safetensors.sh"
else
    echo "Error: $SCRIPTS_DIR/linux_install.sh not found!"
    exit 1
fi

echo "Installation process finished!"
