# AGENTS.md

Guia operacional para agentes de IA no projeto **Enterprise AI Sales Intelligence** (POC Microsoft Azure AI Solution Engineering).

## O que é este repo

POC enterprise-grade de **Sales Intelligence Agent** — combina dados estruturados (CRM, vendas, tickets via MCP) com conhecimento documental (RAG + Azure AI Search) para briefings executivos de vendas.

**Não é um chatbot genérico.** É um agente que decide dinamicamente entre MCP, RAG ou ambos.

Leia antes de codar:

- [`docs/PLAN.md`](docs/PLAN.md) — especificação completa (52 seções)
- [`docs/stack.md`](docs/stack.md) — stack, portas, fases
- [`.env.example`](.env.example) — variáveis de ambiente

## Stack resumida

| Layer | Choice |
|-------|--------|
| Backend | Python 3.12+ · FastAPI · Semantic Kernel · MCP SDK |
| LLM | Microsoft Foundry / Azure OpenAI |
| Retrieval | Azure AI Search (hybrid + vector) |
| Storage | Azure Blob Storage |
| Frontend | Vue 3 · Vite · TypeScript |
| Auth | Microsoft Entra ID (deploy) |
| Observability | Application Insights |
| IaC | Bicep |
| Cloud runtime | Azure Container Apps |
| Local | Docker Compose |
| Tests | pytest · Playwright E2E |

## Workflow do agente

```
brainstorming
  → writing-plans
  → implement (tdd + skills de domínio)
  → verification-before-completion
  → commit (caveman-commit — só quando o usuário pedir)
```

| Fase | Skill | Regra |
|------|-------|-------|
| Design | `brainstorming` | Sem código até design aprovado |
| Plano | `writing-plans` | Salvar em `docs/superpowers/plans/` |
| Build | `tdd` | Red → green; testar nas costuras públicas |
| FastAPI | `fastapi`, `fastapi-templates` | Estrutura async, DI, camadas separadas |
| MCP | `mcp-builder`, `python-mcp-server-generator` | Tools tipadas; boundary sobre REST APIs |
| RAG | `rag-implementation`, `azure-ai` | Hybrid search; citações obrigatórias |
| Azure | `azure-prepare`, `azure-ai`, `azure-storage`, `azure-deploy` | Budget; não hardcodar API versions |
| Vue | `vue-best-practices` | Chat UI, sources, fact vs recommendation |
| Testes Python | `python-testing-patterns` | pytest, mocks, httpx |
| Avaliação LLM | `llm-evaluation` | Dataset em `data/eval/` |
| E2E | `playwright-best-practices` | Mock writes quando possível |
| Debug | `systematic-debugging` | Causa raiz antes de fixes |
| Done | `verification-before-completion` | Rodar testes; evidência; subir stack local |
| Commit | `caveman-commit` | Conventional Commits, English — só quando pedido |

## Mapa tecnologia → skill

| Tecnologia | Skill(s) | Cobertura |
|------------|----------|-----------|
| Microsoft Foundry / Azure OpenAI | `azure-ai` | LLM, embeddings, AI Search SDK |
| Azure AI Search | `azure-ai`, `rag-implementation` | Index, hybrid search, ingestion |
| Azure Blob Storage | `azure-storage` | Document repository |
| Semantic Kernel | — (PLAN.md + docs Microsoft) | **Sem skill dedicada** |
| MCP | `mcp-builder`, `python-mcp-server-generator` | Server Python, tools |
| Python / FastAPI | `fastapi`, `fastapi-templates`, `python-testing-patterns` | API, estrutura, pytest |
| Vue 3 | `vue-best-practices` | Composition API, TS |
| Docker / Compose | — (PLAN.md §30) | **Sem skill dedicada** |
| Azure Container Apps | `azure-deploy` | Deploy containers |
| Bicep / IaC | `azure-prepare` | Módulos, resource group |
| Entra ID | `azure-prepare` (parcial) | Auth — detalhes no PLAN §22 |
| Application Insights | `azure-ai` (parcial) | Telemetria agent |
| Key Vault | `azure-prepare` | Secrets em deploy |
| Playwright E2E | `playwright-best-practices` | Specs Vue |
| LLM evaluation | `llm-evaluation` | Tool selection, grounding |
| Docs + Mermaid | `design-doc-mermaid`, `documentation-and-adrs` | **Sempre** ao documentar fluxos e ADRs |
| Prisma / Next.js | `prisma-*`, `vercel-react-best-practices` | **Não usados neste projeto** |

### Skills herdadas (Faruk Base) — uso limitado

| Skill | Neste projeto |
|-------|---------------|
| `frontend-design`, `hallmark` | UI mínima — não priorizar design |
| `vercel-react-best-practices` | Não aplicável (Vue, não React) |
| `nodejs-backend-patterns` | Não aplicável (Python) |
| `prisma-*` | Não aplicável (sem Prisma) |

## Restore skills após clone

```bash
npx skills experimental_install
```

28 skills em `.agents/skills/` — lock em [`skills-lock.json`](skills-lock.json).

## Fase atual: Phase 1 (vertical slice)

**Não implementar tudo de uma vez.** Primeira entrega:

```text
User → Vue → FastAPI → Semantic Kernel Agent → MCP → CRM API → Answer
```

Inclui: mocks CRM/Sales/Tickets, MCP server, agent básico, chat Vue.

**Somente depois:** Azure OpenAI → AI Search → Blob → Container Apps → Entra/App Insights.

## Regras de arquitetura (obrigatórias)

1. **Separar** orchestration (agent) de HTTP controllers.
2. **MCP** chama REST APIs existentes — não duplicar lógica de negócio.
3. **RAG** para conhecimento documental; **MCP** para dados transacionais.
4. **Citações** em toda resposta RAG; nunca inventar fontes.
5. **FACT** vs **AI RECOMMENDATION** — distinguir na UI e no prompt.
6. **Autorização** derivada da identidade autenticada — nunca confiar só em `customer_id` do frontend.
7. **Não commitar** secrets (`.env`, keys, tokens).
8. **Não declarar** integração Azure OK sem teste contra serviço real.
9. **Budget Azure** — modelos pequenos, alertas, cleanup documentado.

## Estrutura alvo

```
apps/api/app/
├── api/           # Route handlers (thin)
├── agent/         # Semantic Kernel orchestration
├── rag/           # KnowledgeRetriever, ingest
├── mcp/           # MCP client
├── domain/        # Models, business types
└── infrastructure/# Azure clients, telemetry

apps/mcp-server/   # MCP tools → httpx → mock APIs
apps/web/          # Vue 3 chat
services/          # mock-crm, mock-sales, mock-tickets
data/              # ACME demo dataset
infrastructure/azure/bicep/
docs/              # architecture, security, rag, mcp, cost, ADRs
```

## Perguntas ao usuário

Quando a decisão for do usuário e não puder inferir do PLAN:

1. Preferir **AskQuestion** (Cursor) ou bloco copy-paste editável.
2. Uma decisão por mensagem quando possível.
3. **Database gate não se aplica** — este projeto não usa PostgreSQL/Prisma.

### Decisões Azure pendentes (perguntar antes de Phase 2+)

- Subscription / resource group já existente?
- Região preferida (padrão PLAN: `eastus`)?
- Modelos chat + embedding a deployar (nomes exatos)?
- Budget máximo e e-mail para alertas?

## Idioma

- **Commits:** English, Conventional Commits
- **Copy da UI / docs de produto:** Português (demo pode ser EN se preferir entrevista MS)
- **Skills (SKILL.md):** English
- **Respostas ao usuário:** Português

## Git

- Commit **somente** quando o usuário pedir
- Nunca force-push em `main`
- Nunca commitar `.env` ou credenciais

## Testes

| Tipo | Tool | Local |
|------|------|-------|
| Unit | pytest | `apps/api/tests/`, `apps/mcp-server/tests/` |
| Integration | pytest + httpx | Agent → MCP → mock API |
| E2E | Playwright | `apps/web/e2e/` |

E2E **não deve escrever** em Azure real — mockar API ou usar ambiente de teste.

Antes de dizer "pronto": `verification-before-completion`.

## Dev server (fim de task)

Ao concluir task com código executável, **subir stack local sem pedir permissão** se estiver down:

```bash
docker compose up --build
```

| Validação | URL / comando |
|-----------|---------------|
| API | `GET http://localhost:8000/health` |
| Frontend | http://localhost:5173 — título "Enterprise AI Sales Intelligence" |
| MCP | conforme transport configurado |

Informar URLs efetivas ao usuário.

## Documentação (obrigatório manter)

**Este projeto é de aprendizado** — toda feature implementada deve atualizar a doc correspondente.

Índice: [`docs/README.md`](docs/README.md)

| Tipo | Local | Quando atualizar |
|------|-------|------------------|
| Trilha de aprendizado | `docs/learn/01–07` | Novo fluxo ou conceito |
| Deep dives | `docs/architecture.md`, `mcp.md`, `rag.md`, … | Mudança de contrato ou arquitetura |
| ADRs | `docs/adrs/` | Decisão irreversível ou alternativa rejeitada |
| Diagramas | **Mermaid** inline nos `.md` | Sempre que o fluxo mudar |

**Skills para docs:** `design-doc-mermaid`, `documentation-and-adrs`

**Regras Mermaid:** preferir `flowchart` e `sequenceDiagram`; evitar `block-beta`.

**Checklist pós-implementação:**

1. Atualizar guia `learn/` + diagrama de sequência
2. Atualizar deep dive se API ou módulo mudou
3. Novo ADR se decisão arquitetural
4. Nunca deixar doc contradizer código

Arquivos: `architecture.md`, `security.md`, `rag.md`, `mcp.md`, `observability.md`, `cost.md`, ADR-001…006.

## Definition of Done

Checklist completo: [`docs/PLAN.md` §51](docs/PLAN.md#51-definition-of-done).
