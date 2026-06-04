FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

ARG UV_GROUPS="server"

RUN apt-get -y update \
    && apt-get -y install git libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /bin/uv

COPY pyproject.toml uv.lock /app/
COPY client/pyproject.toml /app/client/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --no-dev \
    $(for group in $UV_GROUPS; do printf " --only-group %s" "$group"; done)

FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get -y update \
    && apt-get -y install curl libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY src/alembic.ini /app/alembic.ini
COPY src/migrations /app/migrations
COPY src/app /app/app
