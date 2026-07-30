FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY apps/mcp-server ./apps/mcp-server

RUN uv sync --directory apps/mcp-server

WORKDIR /app/apps/mcp-server
EXPOSE 8001
CMD ["uv", "run", "mcp-server"]
