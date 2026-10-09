# syntax=docker/dockerfile:1
#
# Production image for the FastAPI backend (Section 9.4 - cloud deployment).
# The same image is used by docker-compose.yml locally and by any container
# host, so the runtime a reviewer sees matches the runtime in production.

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# curl is only needed by the HEALTHCHECK below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencies are copied first so Docker can reuse the layer while the source
# code changes.
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY database ./database
COPY scripts ./scripts

# Run as an unprivileged user: a compromised process cannot write to the image.
RUN useradd --create-home --uid 10001 marketplace \
    && chown -R marketplace:marketplace /app

USER marketplace

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
