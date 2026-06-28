FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

ENV PYTHONPATH=/app/src
ENV PATH=/app/.venv/bin:$PATH

CMD ["sh", "-c", "uvicorn core.main:app --host 0.0.0.0 --port 8000"]
