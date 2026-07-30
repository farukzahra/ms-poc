FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY packages/demo_data ./packages/demo_data
COPY services ./services

RUN uv sync --directory services

WORKDIR /app/services
ENV PYTHONPATH=/app/services
CMD ["uv", "run", "python", "runner.py"]
