# DocuLens Enterprise RAG: Production Self-Contained Cloud Container
# Includes embedded Ollama with Qwen 2.5 (1.5B) + FastAPI + Tailwind UI
# 100% Free, Zero External API Keys, Zero Laptop Hardware Dependency
# Compatible with Hugging Face Spaces (Port 7860), Render, and Railway

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_MODELS=/home/user/.ollama/models \
    HOME=/home/user

WORKDIR /home/user/app

# Install system dependencies & Ollama CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user (UID 1000 required by Hugging Face Spaces)
RUN useradd -m -u 1000 user && \
    mkdir -p /home/user/.ollama/models && \
    mkdir -p /home/user/app/data && \
    chown -R user:user /home/user

# Copy application source code
COPY --chown=user:user . /home/user/app

# Ensure full execution & write permissions
RUN chmod -R 777 /home/user/app && \
    chmod -R 777 /home/user/.ollama && \
    chmod +x /home/user/app/start.sh

USER user
EXPOSE 7860

CMD ["./start.sh"]
