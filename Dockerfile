# ========================================================
# Production Dockerfile for Render / Cloud Deployment
# ========================================================
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install minimal system dependencies required for pdfplumber / fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application codebase and assets
COPY . .

# Expose default port (Render will inject $PORT dynamically)
EXPOSE 7860

# Launch FastAPI app with dynamic port binding
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
