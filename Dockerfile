FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn

# Copy source code
COPY src/ src/
COPY api.py .
COPY data/ data/
COPY output/ output/
COPY predict.py .
COPY update_elo.py .

# Pre-compute predictions at build time for faster startup
RUN python -c "from src.auto_predict import run_prediction; run_prediction(); print('Predictions pre-computed')"

EXPOSE 5000

# Production server with optimized settings
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "1", "--timeout-keep-alive", "30"]
