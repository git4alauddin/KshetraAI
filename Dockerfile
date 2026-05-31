# KshetraAI. Small image that runs the API. The pipeline can run inside too.
FROM python:3.11-slim

# libgomp1 is needed by lightgbm at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install deps first so layer caches when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV KSHETRA_BASE=/app
EXPOSE 8000

# default: serve the API. override with `docker run ... python run_pipeline.py` to train.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
