FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml
COPY app/ ./app
COPY tests/ ./tests
EXPOSE 8000
CMD ["fastapi", "run", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]