#!/bin/bash
set -e

if [ -z "$GROQ_API_KEY" ]; then
    echo "=== [1/3] Starting Embedded Ollama Engine inside Cloud Container ==="
    ollama serve &

    echo "=== [2/3] Waiting for Ollama to initialize on port 11434 ==="
    for i in $(seq 1 30); do
        if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
            echo "Ollama initialized successfully!"
            break
        fi
        sleep 1
    done

    echo "=== [3/3] Pulling Open-Weight Model (qwen2.5:1.5b) ==="
    ollama pull qwen2.5:1.5b || true
else
    echo "=== [Cloud LPU Mode] GROQ_API_KEY detected. Skipping local Ollama to conserve memory. ==="
fi

PORT="${PORT:-7860}"
echo "=== Launching DocuLens Enterprise RAG Studio on port $PORT ==="
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
