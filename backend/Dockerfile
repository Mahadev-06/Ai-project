FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for layer caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "." && \
    python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Download models on build (cached in volume)
RUN python -c "from app.services.model_manager import ModelManager; m = ModelManager(); m.load_all()" || true

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
