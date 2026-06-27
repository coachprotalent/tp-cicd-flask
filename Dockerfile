# ---- Stage 1: build dependencies ----
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: final, minimal image ----
FROM python:3.12-slim

# Create an unprivileged user (never run as root)
RUN useradd --create-home --uid 1001 appuser

WORKDIR /app

# Copy only the installed dependencies + the code
COPY --from=builder /install /usr/local
COPY app/ ./app/

# Environment variables
ENV PORT=8000 \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

# Production server (gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]