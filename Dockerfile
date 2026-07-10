# ── devtools — Dockerfile ─────────────────────────────────────────
# Multi-stage build for minimal image size

FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Runtime ─────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install monospace font for screenshot tool
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8080

ENV PORT=8080

CMD ["python3", "devtool.py", "--serve", "--host", "0.0.0.0"]
