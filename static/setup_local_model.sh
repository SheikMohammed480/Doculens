#!/bin/bash
echo "======================================================================"
echo "   DocuLens Enterprise AI: 1-Click Local Model Auto-Setup (Mac/Linux)"
echo "======================================================================"
echo ""

if ! command -v ollama &> /dev/null; then
    echo "[!] Ollama not detected. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "[*] Configuring CORS for web app (OLLAMA_ORIGINS=*)..."
export OLLAMA_ORIGINS="*"

echo "[*] Ensuring model 'qwen2.5:1.5b' is downloaded..."
ollama pull qwen2.5:1.5b

echo ""
echo "======================================================================"
echo "[SUCCESS] Model is downloaded and ready!"
echo "Starting Ollama service on http://127.0.0.1:11434..."
echo "Keep this terminal open while using DocuLens Studio."
echo "======================================================================"
ollama serve
