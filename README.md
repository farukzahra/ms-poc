# Enterprise AI Sales Intelligence Agent

POC **Microsoft Azure AI Solution Engineering** — plataforma de inteligência de vendas com agente de IA que combina dados operacionais (MCP) e conhecimento documental (RAG).

> *"Prepare me for my meeting with ACME."* → briefing executivo com CRM, vendas, tickets, contratos e políticas internas — com citações e distinção fato vs recomendação.

## Status

| Fase | Estado |
|------|--------|
| Especificação | ✅ [`docs/PLAN.md`](docs/PLAN.md) |
| Skills + AGENTS | ✅ |
| Phase 1 — vertical slice local | 🔲 pendente |
| Azure OpenAI / Search / Blob | 🔲 pendente |
| Deploy Container Apps | 🔲 pendente |

## Stack

| Camada | Tecnologia |
|--------|------------|
| Agent | Semantic Kernel + Azure OpenAI |
| Tools | MCP Server → REST APIs mock |
| Knowledge | Azure AI Search + RAG |
| Backend | Python 3.12 · FastAPI |
| Frontend | Vue 3 · Vite · TypeScript |
| Cloud | Azure Container Apps · Blob · Key Vault · Entra ID |
| Observability | Application Insights |

Detalhes: [`docs/stack.md`](docs/stack.md)

## Documentação (aprendizado)

**Comece aqui:** [`docs/README.md`](docs/README.md) — trilha com 7 guias + diagramas Mermaid.

| Trilha | Conteúdo |
|--------|----------|
| [learn/01-concepts](docs/learn/01-concepts.md) | Agent, RAG, MCP, grounding |
| [learn/03-request-flow](docs/learn/03-request-flow.md) | Sequência Vue → API → Agent |
| [architecture.md](docs/architecture.md) | Arquitetura consolidada |
| [adrs/](docs/adrs/) | Decisões arquiteturais (ADR-001…006) |

## Arquitetura (alvo)

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

## Quick start (quando Phase 1 existir)

```bash
cp .env.example .env
docker compose up --build
```

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| Health | http://localhost:8000/health |

## Repositório

```
ms-poc/
├── apps/
│   ├── api/           # FastAPI + agent
│   ├── mcp-server/    # MCP tools
│   └── web/           # Vue 3
├── services/          # mock enterprise APIs
├── data/              # dataset ACME (fictício)
├── infrastructure/    # Bicep Azure
├── docs/
│   ├── PLAN.md        # especificação completa
│   └── stack.md
├── AGENTS.md          # guia para agentes de IA
└── skills-lock.json
```

## Desenvolvimento em fases

1. **Local** — FastAPI + Semantic Kernel + MCP + mocks + Vue
2. **Azure OpenAI** — LLM e tool calling reais
3. **Azure AI Search** — ingestion, hybrid search, citações
4. **Blob Storage** — repositório de documentos
5. **Container Apps** — deploy
6. **Entra ID + Key Vault + App Insights**

Ver [`docs/PLAN.md` §36](docs/PLAN.md#36-development-strategy).

## Agent skills (Cursor)

Restaurar após clone:

```bash
npx skills experimental_install
```

Workflow e mapa tech→skill: [`AGENTS.md`](AGENTS.md).

## Cenários demo

| Pergunta | Esperado |
|----------|----------|
| Prepare me for my meeting with ACME | MCP + RAG |
| How much did ACME spend last year? | MCP only |
| What is our enterprise AI deployment policy? | RAG only |
| What are the biggest risks to ACME's renewal? | MCP + RAG + reasoning |

## Custo Azure

POC orientada a **~$50** com alertas de budget. Ver `docs/cost.md` (a criar) e PLAN §9/§35.

## From POC to Production

O README final incluirá evolução para multi-agent, private endpoints, managed identities, CI/CD e governança — ver [`docs/PLAN.md` §44](docs/PLAN.md#44-production-architecture).

## Licença

Projeto privado — POC de entrevista / demonstração.
