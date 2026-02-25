# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends wait-for-it

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev

COPY . .

ARG USER_ID=1001
ARG GROUP_ID=1001

RUN if ! getent group appuser > /dev/null 2>&1; then \
        groupadd -r appuser -g ${GROUP_ID}; \
    fi && \
    if ! getent passwd appuser > /dev/null 2>&1; then \
        useradd -r -g appuser -u ${USER_ID} appuser; \
    fi

RUN mkdir -p /home/appuser/.cache/uv&& \
    chown -R appuser:appuser /app /home/appuser


USER appuser

RUN mkdir /app/logs &&\
    chown -R appuser:appuser /app/logs

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

CMD ["python", "-m", "consumer"]