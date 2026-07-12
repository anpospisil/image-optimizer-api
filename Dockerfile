FROM python:3.12-slim

# Cache bust
ARG CACHE_BUST=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

COPY . .

CMD ["sh", "-c", "echo PORT=$PORT && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]