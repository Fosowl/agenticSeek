#!/usr/bin/env bash

pip3 install --upgrade packaging
pip3 install --upgrade pip setuptools
curl -fsSL https://ollama.com/install.sh | sh
pip3 install -r requirements.txt