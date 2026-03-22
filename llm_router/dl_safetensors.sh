##########
# Dummy script to download the model
# Because downloading with hugging face does not seem to work, maybe I am doing something wrong?
# AdaptiveClassifier.from_pretrained("adaptive-classifier/llm-router") ----> result in config.json not found
# Therefore, I put all the files in llm_router and download the model file with this script, If you know a better way please raise an issue
#########

#!/usr/bin/env bash

# Define the URL and filename
URL="https://huggingface.co/adaptive-classifier/llm-router/resolve/main/model.safetensors"
FILENAME="model.safetensors"

if [ ! -f "$FILENAME" ]; then
    echo "Router safetensors file not found, downloading..."
    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$FILENAME" "$URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "$FILENAME" "$URL"
    else
        echo "Error: Neither curl nor wget is available. Please install one of them."
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "Download completed successfully"
    else
        echo "Download failed"
        exit 1
    fi
else
    echo "File already exists, skipping download"
fi
