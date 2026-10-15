#!/usr/bin python3

import argparse
import time
from flask import Flask, jsonify, request

from sources.llamacpp_handler import LlamacppLLM
from sources.ollama_handler import OllamaLLM

parser = argparse.ArgumentParser(description='AgenticSeek server script')
parser.add_argument('--provider', type=str, help='LLM backend library to use. set to [ollama], [vllm] or [llamacpp]', required=True)
parser.add_argument('--port', type=int, help='port to use', required=True)
args = parser.parse_args()

app = Flask(__name__)

assert args.provider in ["ollama", "llamacpp"], f"Provider {args.provider} does not exists. see --help for more information"

handler_map = {
    "ollama": OllamaLLM(),
    "llamacpp": LlamacppLLM(),
}

generator = handler_map[args.provider]

@app.route('/generate', methods=['POST'])
def start_generation():
    if generator is None:
        return jsonify({"error": "Generator not initialized"}), 401
    data = request.get_json()
    history = data.get('messages', [])
    if generator.start(history):
        return jsonify({"message": "Generation started"}), 202
    return jsonify({"error": "Generation already in progress"}), 402

@app.route('/setup', methods=['POST'])
def setup():
    data = request.get_json()
    model = data.get('model', None)
    if model is None:
        return jsonify({"error": "Model not provided"}), 403
    generator.set_model(model)
    return jsonify({"message": "Model set"}), 200

@app.route('/get_updated_sentence')
def get_updated_sentence():
    if not generator:
        return jsonify({"error": "Generator not initialized"}), 405
    print(generator.get_status())
    return generator.get_status()

if __name__ == '__main__':
    # Never debug=True: the Werkzeug debugger is remote code execution on 0.0.0.0.
    app.run(host='0.0.0.0', threaded=True, debug=False, port=args.port)