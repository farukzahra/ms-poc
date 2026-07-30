FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY packages/demo_data ./packages/demo_data
COPY services ./services
COPY apps/api ./apps/api
COPY data ./data
COPY prompts ./prompts

RUN uv sync --directory apps/api

WORKDIR /app/apps/api
ENV PYTHONPATH=/app/apps/api
ENV DATA_DIR=/app/data
ENV PROMPTS_DIR=/app/prompts
EXPOSE 8000
CMD ["uv", "run", "enterprise-api"]
