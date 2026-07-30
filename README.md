# Enterprise AI Sales Intelligence Agent

**Microsoft Azure AI Solution Engineering** POC — sales intelligence platform with an AI agent that combines operational data (MCP) and document knowledge (RAG).

> *"Prepare me for my meeting with ACME."* → executive briefing with CRM, sales, tickets, contracts, and internal policies — with citations and FACT vs AI RECOMMENDATION labels.

## Status

| Phase | State |
|-------|-------|
| Specification | ✅ [`docs/PLAN.md`](docs/PLAN.md) |
| Skills + AGENTS | ✅ |
| Phase 1 — local vertical slice | ✅ `docker compose up` |
| Phase 2 — Azure OpenAI | ✅ env-gated (`AzureSalesAgent`) |
| Phase 3 — Azure AI Search RAG | ✅ env-gated + local fallback |
| Phase 4 — Blob Storage | ✅ env-gated sync hook |
| Phase 5 — Container Apps | ✅ Bicep skeleton |
| Phase 6 — Entra + Insights | ✅ env-gated hooks |

## Stack

| Layer | Technology |
|-------|------------|
| Agent | Semantic Kernel + Azure OpenAI |
| Tools | MCP Server → mock REST APIs |
| Knowledge | Azure AI Search + RAG |
| Backend | Python 3.12 · FastAPI |
| Frontend | Vue 3 · Vite · TypeScript |
| Cloud | Azure Container Apps · Blob · Key Vault · Entra ID |
| Observability | Application Insights |

Details: [`docs/stack.md`](docs/stack.md)

## Documentation (learning)

**Start here:** [`docs/README.md`](docs/README.md) — 7 guides + Mermaid diagrams.

| Path | Content |
|------|---------|
| [learn/01-concepts](docs/learn/01-concepts.md) | Agent, RAG, MCP, grounding |
| [learn/03-request-flow](docs/learn/03-request-flow.md) | Vue → API → Agent sequence |
| [architecture.md](docs/architecture.md) | Consolidated architecture |
| [adrs/](docs/adrs/) | Architecture decisions (ADR-001…006) |

## Target architecture

```text
                     SALES USER
                          │
                          ▼
                   Vue 3 UI (chat)
                          │
                          ▼
              FastAPI + Semantic Kernel Agent
                     /            \
                    ▼              ▼
                 RAG            MCP Client
                   │              │
                   ▼              ▼
           Azure AI Search    MCP Server
                   │              │
                   ▼              ▼
            Blob Storage    Mock CRM / Sales / Tickets
                   │
                   ▼
           Azure OpenAI (Foundry)
```

## Quick start

```bash
cp .env.example .env
python -m uv sync --all-packages   # or: pip install uv && uv sync --all-packages
docker compose up --build -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5200 |
| API | http://localhost:8000 |
| MCP | http://localhost:8001/mcp |
| Health | http://localhost:8000/health |

**Demo prompt:** `Prepare me for my meeting with ACME`

```bash
make test          # pytest
make test-e2e      # Playwright (starts Vite on :5200)
make ingest        # local or Azure RAG ingest
```

## Repository layout

```
ms-poc/
├── apps/
│   ├── api/           # FastAPI + agent
│   ├── mcp-server/    # MCP tools
│   └── web/           # Vue 3
├── services/          # mock enterprise APIs
├── data/              # fictional ACME dataset
├── infrastructure/    # Azure Bicep
├── docs/
│   ├── PLAN.md        # full specification
│   └── stack.md
├── AGENTS.md          # guide for AI agents
└── skills-lock.json
```

## Development phases

1. **Local** — FastAPI + Semantic Kernel + MCP + mocks + Vue
2. **Azure OpenAI** — real LLM and tool calling
3. **Azure AI Search** — ingestion, hybrid search, citations
4. **Blob Storage** — document repository
5. **Container Apps** — deploy
6. **Entra ID + Key Vault + App Insights**

See [`docs/PLAN.md` §36](docs/PLAN.md#36-development-strategy).

## Agent skills (Cursor)

Restore after clone:

```bash
npx skills experimental_install
```

Workflow and tech→skill map: [`AGENTS.md`](AGENTS.md).

## Demo scenarios

| Question | Expected |
|----------|----------|
| Prepare me for my meeting with ACME | MCP + RAG |
| How much did ACME spend last year? | MCP only |
| What is our enterprise AI deployment policy? | RAG only |
| What are the biggest risks to ACME's renewal? | MCP + RAG + reasoning |

## Azure cost

POC targets **~$50** with budget alerts. See [`docs/cost.md`](docs/cost.md) and PLAN §9/§35.

## From POC to Production

Evolution to multi-agent, private endpoints, managed identities, CI/CD, and governance — [`docs/PLAN.md` §44](docs/PLAN.md#44-production-architecture).

## Language

**English only** for all repo content (docs, UI, comments). See [`.cursor/rules/english-only.mdc`](.cursor/rules/english-only.mdc).

## License

Private project — interview / demonstration POC.
