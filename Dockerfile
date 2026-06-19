FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache
COPY . .

ARG VERSION=dev
ARG APP_VERSION=${VERSION}
ENV APP_VERSION=${APP_VERSION}
EXPOSE 8000

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
