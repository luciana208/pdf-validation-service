# etapa de build: resuelve dependencias con uv en un venv aislado
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# etapa final: solo python, el venv y el codigo, sin uv ni herramientas de build
FROM python:3.14-slim

ENV TZ=America/Argentina/Buenos_Aires \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    GRANIAN_INTERFACE=asgi \
    GRANIAN_HOST=0.0.0.0 \
    GRANIAN_PORT=8000 \
    GRANIAN_WORKERS=1

# parches del sistema, zona horaria, usuario sin privilegios y sin pip
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home --shell /usr/sbin/nologin appuser \
    && pip uninstall -y pip

WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup app ./app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-m", "app.infrastructure.healthcheck_cli"]

# granian toma host, puerto y workers de las variables GRANIAN_*
CMD ["granian", "app.main:app"]
