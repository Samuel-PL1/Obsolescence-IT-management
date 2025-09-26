# Multi-stage is optional; keep it simple and fast
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (if needed for pandas/openpyxl performance)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Expose the port Flask will bind to (via PORT env)
EXPOSE 8080

CMD ["python", "src/main.py"]
