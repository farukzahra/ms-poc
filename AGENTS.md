# AGENTS.md

Operational guide for AI agents working on **Enterprise AI Sales Intelligence** (Microsoft Azure AI Solution Engineering POC).

## What this repo is

Enterprise-grade **Sales Intelligence Agent** POC — combines structured data (CRM, sales, tickets via MCP) with document knowledge (RAG + Azure AI Search) for executive sales briefings.

**Not a generic chatbot.** The agent dynamically chooses MCP, RAG, or both.

Read before coding:

- [`docs/PLAN.md`](docs/PLAN.md) — full specification (52 sections)
- [`docs/stack.md`](docs/stack.md) — stack, ports, phases
- [`.env.example`](.env.example) — environment variables

## Language (mandatory)

**Everything in this repository is English-only.**

| Artifact | Language |
|----------|----------|
| Documentation (`docs/`, README, ADRs) | **English** |
| UI copy, errors, demo labels | **English** |
| Code comments | **English** |
| Commit messages | **English** (Conventional Commits) |
| Cursor rule | [`.cursor/rules/english-only.mdc`](.cursor/rules/english-only.mdc) |

## Stack summary

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

## Agent workflow

```
brainstorming
  → writing-plans
  → implement (tdd + domain skills)
  → verification-before-completion
  → commit (caveman-commit — only when user asks)
```

| Phase | Skill | Rule |
|-------|-------|------|
| Design | `brainstorming` | No code until design approved |
| Plan | `writing-plans` | Save to `docs/superpowers/plans/` |
| Build | `tdd` | Red → green; test at public seams |
| FastAPI | `fastapi`, `fastapi-templates` | Async structure, DI, layered |
| MCP | `mcp-builder`, `python-mcp-server-generator` | Typed tools; REST boundary |
| RAG | `rag-implementation`, `azure-ai` | Hybrid search; citations required |
| Azure | `azure-prepare`, `azure-ai`, `azure-storage`, `azure-deploy` | Budget; no hardcoded API versions |
| Vue | `vue-best-practices` | Chat UI, sources, fact vs recommendation |
| Python tests | `python-testing-patterns` | pytest, mocks, httpx |
| LLM eval | `llm-evaluation` | Dataset in `data/eval/` |
| E2E | `playwright-best-practices` | Mock writes when possible |
| Debug | `systematic-debugging` | Root cause before fixes |
| Done | `verification-before-completion` | Run tests; evidence; start local stack |
| Commit | `caveman-commit` | English Conventional Commits — only when asked |
| Docs | `design-doc-mermaid`, `documentation-and-adrs` | **Always** when documenting flows / ADRs |

## Technology → skill map

| Technology | Skill(s) | Coverage |
|------------|----------|----------|
| Microsoft Foundry / Azure OpenAI | `azure-ai` | LLM, embeddings, AI Search SDK |
| Azure AI Search | `azure-ai`, `rag-implementation` | Index, hybrid search, ingestion |
| Azure Blob Storage | `azure-storage` | Document repository |
| Semantic Kernel | — (PLAN.md + Microsoft docs) | **No dedicated skill** |
| MCP | `mcp-builder`, `python-mcp-server-generator` | Python server, tools |
| Python / FastAPI | `fastapi`, `fastapi-templates`, `python-testing-patterns` | API, structure, pytest |
| Vue 3 | `vue-best-practices` | Composition API, TS |
| Docker / Compose | — (PLAN.md §30) | **No dedicated skill** |
| Azure Container Apps | `azure-deploy` | Container deploy |
| Bicep / IaC | `azure-prepare` | Modules, resource group |
| Entra ID | `azure-prepare` (partial) | Auth — PLAN §22 |
| Application Insights | `azure-ai` (partial) | Agent telemetry |
| Key Vault | `azure-prepare` | Deploy secrets |
| Playwright E2E | `playwright-best-practices` | Vue specs |
| LLM evaluation | `llm-evaluation` | Tool selection, grounding |
| Prisma / Next.js | `prisma-*`, `vercel-react-best-practices` | **Not used in this project** |

### Inherited skills (Faruk Base) — limited use

| Skill | In this project |
|-------|-----------------|
| `frontend-design`, `hallmark` | Minimal UI — do not prioritize design |
| `vercel-react-best-practices` | N/A (Vue, not React) |
| `nodejs-backend-patterns` | N/A (Python) |
| `prisma-*` | N/A (no Prisma) |

## Restore skills after clone

```bash
npx skills experimental_install
```

30 skills in `.agents/skills/` — lock in [`skills-lock.json`](skills-lock.json).

## Current phase: Phase 1 (vertical slice)

**Do not implement everything at once.** First delivery:

```text
User → Vue → FastAPI → Semantic Kernel Agent → MCP → CRM API → Answer
```

Includes: mock CRM/Sales/Tickets, MCP server, basic agent, Vue chat.

**Only after that:** Azure OpenAI → AI Search → Blob → Container Apps → Entra/App Insights.

## Architecture rules (mandatory)

1. **Separate** orchestration (agent) from HTTP controllers.
2. **MCP** calls existing REST APIs — no duplicated business logic.
3. **RAG** for document knowledge; **MCP** for transactional data.
4. **Citations** on every RAG-influenced answer; never invent sources.
5. **FACT** vs **AI RECOMMENDATION** — distinguish in UI and prompt.
6. **Authorization** from authenticated identity — never trust frontend `customer_id` alone.
7. **Do not commit** secrets (`.env`, keys, tokens).
8. **Do not claim** Azure integration works without testing against real services.
9. **Azure budget** — small models, alerts, cleanup documented.

## Target structure

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

## Asking the user

When the decision is the user's and cannot be inferred from the PLAN:

1. Prefer **AskQuestion** (Cursor) or an editable copy-paste block.
2. One decision per message when possible.
3. **Database gate does not apply** — no PostgreSQL/Prisma in this project.

### Automate before manual steps

Before asking the user for **any manual action** (browser click, install, DNS, create token):

1. **Try to execute yourself** — PAT, SSH, API, `gh`, deploy scripts, documented credentials.
2. **Check known credential locations** — `C:\repo\financeiro\planos\vps-secrets\`, `secrets.local.md`, `.env.example`.
3. **Azure** — install Azure CLI if missing; run `az login` (or service principal from `vps-secrets/`); use [`scripts/azure-discover.ps1`](scripts/azure-discover.ps1) and [`scripts/azure-fill-env.ps1`](scripts/azure-fill-env.ps1). See [`docs/azure-access.md`](docs/azure-access.md).
4. **Privileges before asking** — tell the user which **RBAC role/scope** unlocks full agent automation; only ask for manual steps when impossible even with those privileges (first login, OAuth/2FA, billing quota, Entra admin consent).
5. Escalate only when automation is impossible — state exactly what to create (token type, scope, secret name).

Cursor rule: [`.cursor/rules/automate-before-manual.mdc`](.cursor/rules/automate-before-manual.mdc).

## Git

- Commit **only** when the user asks
- Never force-push to `main`
- Never commit `.env` or credentials

## Testing

| Type | Tool | Location |
|------|------|----------|
| Unit | pytest | `apps/api/tests/`, `apps/mcp-server/tests/` |
| Integration | pytest + httpx | Agent → MCP → mock API |
| E2E | Playwright | `apps/web/e2e/` |

E2E must **not write** to real Azure — mock API or dedicated test env.

Before saying "done": `verification-before-completion`.

## Dev server (end of task)

When finishing a task with runnable code, **start the local stack without asking** if it is down:

```bash
docker compose up --build
```

| Validation | URL / command |
|------------|---------------|
| API | `GET http://localhost:8000/health` |
| Frontend | http://localhost:5173 — title "Enterprise AI Sales Intelligence" |
| MCP | per configured transport |

Report effective URLs to the user.

## Documentation (mandatory maintenance)

**This is a learning project** — every implemented feature must update the matching doc.

Index: [`docs/README.md`](docs/README.md)

| Type | Location | When to update |
|------|----------|----------------|
| Learning path | `docs/learn/01–07` | New flow or concept |
| Deep dives | `docs/architecture.md`, `mcp.md`, `rag.md`, … | Contract or architecture change |
| ADRs | `docs/adrs/` | Irreversible decision or rejected alternative |
| Diagrams | **Mermaid** inline in `.md` | Whenever the flow changes |

**Doc skills:** `design-doc-mermaid`, `documentation-and-adrs`

**Mermaid rules:** prefer `flowchart` and `sequenceDiagram`; avoid `block-beta`.

**Post-implementation checklist:**

1. Update `learn/` guide + sequence diagram
2. Update deep dive if API or module changed
3. New ADR if architectural decision
4. Never leave docs contradicting code

Files: `architecture.md`, `security.md`, `rag.md`, `mcp.md`, `observability.md`, `cost.md`, ADR-001…006.

## Definition of Done

Full checklist: [`docs/PLAN.md` §51](docs/PLAN.md#51-definition-of-done).
