# pb-coach — imagen con uv. Dos targets:
#   runtime (por defecto): solo dependencias de producción, sirve la API.
#   test: añade el grupo dev y corre pytest dentro del contenedor.

FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.12.22 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero (capa cacheada mientras no cambie uv.lock).
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY methodology ./methodology

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"


FROM base AS test

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY tests ./tests

CMD ["pytest", "-q"]


FROM base AS runtime

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/data \
    && chown app:app /app/data
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "pb_coach.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
