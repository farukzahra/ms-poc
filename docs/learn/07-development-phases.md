# 07 — Development Phases

Implementation roadmap — **never all at once**. Each phase leaves the system runnable.

## Timeline visual

```mermaid
flowchart LR
    P1[Phase 1<br/>Vertical slice] --> P2[Phase 2<br/>Azure OpenAI]
    P2 --> P3[Phase 3<br/>AI Search RAG]
    P3 --> P4[Phase 4<br/>Blob Storage]
    P4 --> P5[Phase 5<br/>Container Apps]
    P5 --> P6[Phase 6<br/>Entra + Insights + KV]

    classDef local fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    classDef azure fill:#BBDEFB,stroke:#1565C0,color:#0D47A1
    classDef deploy fill:#FFF3E0,stroke:#E65100,color:#BF360C
    class P1 local
    class P2,P3,P4 azure
    class P5,P6 deploy
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

- [x] `docker compose up` starts everything
- [x] `POST /api/v1/chat` returns CRM data via MCP
- [x] Basic Vue chat
- [x] pytest: agent → MCP → mock API
- [x] Azure OpenAI agent (Semantic Kernel) with MCP tool calling

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
    Data["data/"] --> Ingest --> Search[(AI Search)]
    SK --> RAG --> Search

    classDef p3 fill:#E1BEE7,stroke:#6A1B9A,color:#4A148C
    class Search,RAG p3
```

**Deliverables:**

- [x] `python -m app.rag.ingest`
- [x] `KnowledgeRetriever.search(query, customer_id?)`
- [x] Citations in API response + Vue sources panel
- [x] Hybrid vector + keyword search (Azure)
- [x] Scenarios 3 and 1 partial

## Phase 4 — Blob Storage ✅

**Change:** Blob = document source of truth (local `data/` for dev mirror)

- [x] Upload script + sync on startup + re-ingest to Search

**Ingestion details** (when it runs, where data persists, local fallback): [03 — Request Flow § Document ingestion](03-request-flow.md#document-ingestion-rag-pipeline) and [05 — Azure Services § RAG ingestion lifecycle](05-azure-services.md#rag-ingestion-lifecycle).

## Phase 5 — Azure Container Apps ✅

**Deploy:** FastAPI container, Bicep modules, `/health` for probes

- [x] Bicep: monitoring, storage, search, key vault, ACR, container apps with probes
- [x] `scripts/deploy-azure.sh`

## Phase 6 — Entra ID + Key Vault + Application Insights ✅

**Add:** JWT auth (JWKS), secret refs, agent execution telemetry

- [x] Entra JWT validation with JWKS
- [x] Key Vault Bicep module
- [x] AgentTracer spans + token logging

## Definition of Done — checklist

See [PLAN.md §51](../PLAN.md#51-definition-of-done) — 22 items.

## Rules during implementation

```mermaid
flowchart TD
    R1[Keep app runnable after each PR] --> R2[No placeholder claiming Azure works]
    R2 --> R3["Update docs/learn when flow changes"]
    R3 --> R4[Add ADR on irreversible decisions]
    R4 --> R5[Run tests before done]

    classDef rule fill:#FFF9C4,stroke:#F9A825,color:#E65100
    class R1,R2,R3,R4,R5 rule
```

## Next step

Implement **Phase 1** — start with `writing-plans` → plan in `docs/superpowers/plans/`.

Back to index: [docs/README.md](../README.md)
