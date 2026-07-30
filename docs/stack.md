# Stack — Enterprise AI Sales Intelligence

Stack definido para a POC Microsoft Azure AI Solution Engineering. Detalhes completos em [`PLAN.md`](PLAN.md).

## Overview

| Layer | Choice |
|-------|--------|
| **Backend** | Python 3.12+ · FastAPI · Pydantic · Semantic Kernel |
| **AI / LLM** | Microsoft Foundry / Azure OpenAI (chat + embeddings) |
| **Retrieval** | Azure AI Search (hybrid + vector + semantic ranking) |
| **Agent tools** | MCP Python SDK · MCP Server (stdio ou streamable-http) |
| **Documents** | Azure Blob Storage → ingestion pipeline → AI Search |
| **Frontend** | Vue 3 · Vite · TypeScript |
| **Auth** | Microsoft Entra ID (deploy) · mock/dev auth local |
| **Observability** | Application Insights · Azure Monitor |
| **Secrets** | `.env` local · Azure Key Vault (deploy) |
| **IaC** | Bicep (`infrastructure/azure/bicep/`) |
| **Runtime (cloud)** | Azure Container Apps |
| **Local dev** | Docker · Docker Compose |
| **Unit / integration** | pytest · httpx |
| **E2E** | Playwright (Vue) |
| **Versioning** | `docs/release-history.json` |

## Monorepo layout

```
ms-poc/
├── apps/
│   ├── api/              # FastAPI + Semantic Kernel agent
│   ├── mcp-server/       # MCP tools → mock enterprise APIs
│   └── web/              # Vue 3 chat UI
├── services/
│   ├── mock-crm/
│   ├── mock-sales/
│   └── mock-tickets/
├── data/                 # Sample documents (fictional ACME dataset)
├── infrastructure/azure/
├── docs/
└── docker-compose.yml
```

## Portas locais (padrão)

| Serviço | Porta | Health |
|---------|-------|--------|
| Vue (`apps/web`) | 5173 | título da app |
| FastAPI (`apps/api`) | 8000 | `GET /health`, `GET /ready` |
| MCP Server | 8001 | depende do transport |
| Mock CRM | 8101 | `GET /health` |
| Mock Sales | 8102 | `GET /health` |
| Mock Tickets | 8103 | `GET /health` |

## Fases de implementação

Ver [`PLAN.md` §36](PLAN.md#36-development-strategy):

1. **Local slice** — FastAPI + Semantic Kernel + MCP + mocks + Vue
2. **Azure OpenAI** — LLM real, tool calling
3. **Azure AI Search** — ingestion, RAG, citações
4. **Blob Storage** — fonte de documentos
5. **Container Apps** — deploy API
6. **Entra ID + Key Vault + App Insights**

## Princípios

- LLM **orquestra**; não é a base de conhecimento.
- RAG para documentos; MCP para dados transacionais.
- Não declarar integração Azure funcionando até testar contra o serviço real.
- Budget Azure documentado em `docs/cost.md` (budget ~$50 POC).

## Skills do agente (Cursor)

Mapa completo em [`AGENTS.md`](../AGENTS.md). Principais:

- Workflow: `brainstorming` → `writing-plans` → `tdd` → `verification-before-completion`
- Azure: `azure-ai`, `azure-storage`, `azure-deploy`, `azure-prepare`
- Backend: `fastapi`, `fastapi-templates`, `python-testing-patterns`
- AI: `rag-implementation`, `llm-evaluation`, `mcp-builder`, `python-mcp-server-generator`
- Frontend: `vue-best-practices`
- E2E: `playwright-best-practices`
