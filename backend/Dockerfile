FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source
COPY backend /app/backend
WORKDIR /app/backend

ENV PORT=5000
EXPOSE 5000

# Use shell form so the $PORT environment variable (set by Railway or other hosts) is respected.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} 'app:create_app()'"]
