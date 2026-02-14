# syntax=docker/dockerfile:1.6

FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

COPY src ./src
COPY artifacts ./artifacts


FROM python:3.13-slim AS runtime

ARG SERVER_OPENAPI="{}"

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH="/app"

WORKDIR /app

RUN groupadd --gid 5000 app \
    && useradd --uid 5000 --gid 5000 --create-home --shell /usr/sbin/nologin app

COPY --from=builder --chown=5000:5000 /app/.venv /app/.venv
COPY --from=builder --chown=5000:5000 /app/src ./src
COPY --from=builder --chown=5000:5000 /app/artifacts ./artifacts
COPY --chown=5000:5000 pyproject.toml uv.lock README.md ./

RUN mkdir -p /app/data/.dspy_cache && chown -R 5000:5000 /app

LABEL server.openapi="${SERVER_OPENAPI}"

EXPOSE 8080

USER 5000:5000

CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
