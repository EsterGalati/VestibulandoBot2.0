# ===== base =====
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# ===== deps =====
FROM base AS deps
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt \
    && pip install gunicorn

# ===== app =====
FROM deps AS app
RUN mkdir -p /data && useradd -ms /bin/bash appuser && chown -R appuser:appuser /data /app
USER appuser

COPY --chown=appuser:appuser . /app

EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "8", "--timeout", "60", "-b", "0.0.0.0:8000", "wsgi:app"]
