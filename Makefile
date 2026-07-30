.PHONY: install sync up down test test-e2e ingest health upload-blob deploy-azure

install:
	uv sync --directory apps/api
	uv sync --directory apps/mcp-server
	uv sync --directory services
	cd apps/web && npm install

sync:
	uv sync --directory apps/api
	uv sync --directory apps/mcp-server
	uv sync --directory services

up:
	docker compose up --build -d

down:
	docker compose down

health:
	curl -sf http://localhost:8000/health
	curl -sf http://localhost:8000/ready
	curl -sf http://localhost:8101/health

test:
	cd apps/api && uv run pytest -q

test-e2e:
	cd apps/web && npm run test:e2e

ingest:
	cd apps/api && uv run python -m app.rag.ingest

upload-blob:
	uv run python scripts/upload_documents_to_blob.py

deploy-azure:
	sh scripts/deploy-azure.sh
