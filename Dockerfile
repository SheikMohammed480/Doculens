# DocuLens Enterprise RAG: Production Self-Contained Cloud Container
# Includes embedded Ollama with Qwen 2.5 (1.5B) + FastAPI + Tailwind UI
# 100% Free, Zero External API Keys, Zero Laptop Hardware Dependency
# Compatible with Hugging Face Spaces (Port 7860), Render, and Railway

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    OLLAMA_HOST=127.0.0.1:11434

WORKDIR /app

# Install system dependencies & Ollama CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Grant execute permissions to startup script
RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]
