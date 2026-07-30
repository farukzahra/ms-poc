# 07 — Development Phases

Implementation roadmap — **never all at once**. Each phase leaves the system runnable.

## Timeline visual

```mermaid
gantt
    title POC Implementation Phases
    dateFormat YYYY-MM-DD
    section Local
    Phase 1 Vertical slice     :p1, 2026-07-30, 14d
    section Azure AI
    Phase 2 OpenAI             :p2, after p1, 7d
    Phase 3 AI Search RAG      :p3, after p2, 10d
    Phase 4 Blob Storage       :p4, after p3, 5d
    section Deploy
    Phase 5 Container Apps     :p5, after p4, 7d
    Phase 6 Entra Insights KV  :p6, after p5, 7d
```

## Phase 1 — Local vertical slice ✅ target first

**Stack:** FastAPI + Semantic Kernel + MCP (HTTP) + mock APIs + Vue

```mermaid
flowchart LR
    Vue --> API --> SK --> MCP --> CRM

    classDef p1 fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Vue,API,SK,MCP,CRM p1
```

**Deliverables:**

- [ ] `docker compose up` starts everything
- [ ] `POST /api/v1/chat` returns CRM data via MCP
- [ ] Basic Vue chat
- [ ] pytest: agent → MCP → mock API
- [ ] Mock LLM or deterministic response (no Azure yet)

**Recorded decisions:**

- Python: **uv**
- MCP transport: **streamable-http :8001**
- UI language: **English**

## Phase 2 — Azure OpenAI

**Add:** real LLM, tool calling, agent reasoning

```mermaid
flowchart LR
    SK --> OAI[Azure OpenAI]
    SK --> MCP

    classDef p2 fill:#BBDEFB,stroke:#1565C0,color:#0D47A1
    class OAI p2
```

**Validate:**

- Chat completions work
- Tool calling selects MCP tools
- Token usage logged (prep for Insights)

**Gate:** `az login` + deployments created + `.env` filled — **test against real service**

## Phase 3 — Azure AI Search + RAG

**Add:** ingestion, embeddings, hybrid search, citations

```mermaid
flowchart LR
    Data[data/] --> Ingest --> Search[(AI Search)]
    SK --> RAG --> Search

    classDef p3 fill:#E1BEE7,stroke:#6A1B9A,color:#4A148C
    class Search,RAG p3
```

**Deliverables:**

- [ ] `python -m app.rag.ingest`
- [ ] `KnowledgeRetriever.search(query, customer_id?)`
- [ ] Citations in API response + Vue sources panel
- [ ] Scenarios 3 and 1 partial

## Phase 4 — Blob Storage

**Change:** Blob = document source of truth (local `data/` for dev mirror)

## Phase 5 — Azure Container Apps

**Deploy:** FastAPI container, Bicep modules, `/health` for probes

## Phase 6 — Entra ID + Key Vault + Application Insights

**Add:** JWT auth, secret refs, full agent execution telemetry

## Definition of Done — checklist

See [PLAN.md §51](../PLAN.md#51-definition-of-done) — 22 items.

## Rules during implementation

```mermaid
flowchart TD
    R1[Keep app runnable after each PR] --> R2[No placeholder claiming Azure works]
    R2 --> R3[Update docs/learn when flow changes]
    R3 --> R4[Add ADR on irreversible decisions]
    R4 --> R5[Run tests before done]

    classDef rule fill:#FFF9C4,stroke:#F9A825,color:#E65100
    class R1,R2,R3,R4,R5 rule
```

## Next step

Implement **Phase 1** — start with `writing-plans` → plan in `docs/superpowers/plans/`.

Back to index: [docs/README.md](../README.md)
