# syntax=docker/dockerfile:1
# Build context: the backend/ directory.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# System libraries WeasyPrint needs (Pango/Cairo/GDK-Pixbuf) + Hebrew-capable fonts for PDF output.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libpangoft2-1.0-0 \
      libcairo2 \
      libgdk-pixbuf-2.0-0 \
      shared-mime-info \
      fonts-dejavu-core \
      fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app/backend

# Install runtime dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . ./

ENV PATH="/app/backend/.venv/bin:$PATH"

RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status == 200 else 1)"

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
