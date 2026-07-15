# ---- builder: install the project + its runtime deps into a prefix ----
FROM python:3.12-slim AS builder
WORKDIR /build
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
COPY pyproject.toml ./
COPY app ./app
COPY eval ./eval
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install .

# ---- final: slim runtime image, non-root, no build tooling ----
FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser
COPY --from=builder /install /usr/local
WORKDIR /app
RUN chown appuser:appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
