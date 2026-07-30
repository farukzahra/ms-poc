# 03 — Request Flow

End-to-end flow from user question to response — the heart of the system.

## Vertical slice — Phase 1 (MCP only)

First working delivery **without Azure** — proves Vue → Agent → MCP → CRM.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Sales Rep
    participant Vue as Vue 3 Chat
    participant API as FastAPI
    participant SK as Semantic Kernel Agent
    participant MCP as MCP Server :8001
    participant CRM as Mock CRM :8101

    User->>Vue: "Who is ACME?"
    Vue->>API: POST /api/v1/chat<br/>{message, conversationId}
    API->>SK: run_agent(message, context)
    SK->>SK: classify intent → needs MCP
    SK->>MCP: tool: get_customer("ACME-001")
    MCP->>CRM: GET /customers/ACME-001
    CRM-->>MCP: JSON customer profile
    MCP-->>SK: tool result
    SK->>SK: synthesize answer (Azure OpenAI)
    SK-->>API: answer + toolsUsed
    API-->>Vue: JSON response
    Vue-->>User: render message + tools badge
```

## Full flow — Phase 3+ (MCP + RAG + Azure OpenAI)

Executive briefing: *"Prepare me for my meeting with ACME."*

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Sales Rep
    participant Vue as Vue 3
    participant API as FastAPI
    participant SK as Agent (SK)
    participant OAI as Azure OpenAI
    participant MCP as MCP Server
    participant CRM as CRM API
    participant Sales as Sales API
    participant Tkt as Tickets API
    participant RAG as KnowledgeRetriever
    participant Search as Azure AI Search

    User->>Vue: Prepare me for ACME meeting
    Vue->>API: POST /api/v1/chat
    API->>SK: run_agent()

    Note over SK,OAI: LLM call #1 — plan tools
    SK->>OAI: chat + tool definitions
    OAI-->>SK: call get_customer, get_sales, get_tickets, search RAG

    par MCP parallel calls
        SK->>MCP: get_customer(ACME-001)
        MCP->>CRM: GET /customers/ACME-001
        CRM-->>MCP: profile
        MCP-->>SK: customer data
    and
        SK->>MCP: get_customer_sales(ACME-001)
        MCP->>Sales: GET /customers/.../sales
        Sales-->>MCP: $2.4M, -12% trend
        MCP-->>SK: sales data
    and
        SK->>MCP: get_customer_tickets(ACME-001)
        MCP->>Tkt: GET /customers/.../tickets
        Tkt-->>MCP: 3 open tickets
        MCP-->>SK: tickets data
    end

    SK->>RAG: search(query, customer_id=ACME-001)
    RAG->>OAI: embed query
    OAI-->>RAG: vector
    RAG->>Search: hybrid search + filter
    Search-->>RAG: contract-acme.pdf, renewal-policy.md
    RAG-->>SK: top-K + citations

    Note over SK,OAI: LLM call #2 — synthesize briefing
    SK->>OAI: context from MCP + RAG
    OAI-->>SK: executive briefing

    SK-->>API: answer, sources, toolsUsed, debug (provenance)
    API-->>Vue: JSON
    Vue-->>User: briefing + provenance panel (MCP / RAG / LLM)
```

## API contract — POST /api/v1/chat

```mermaid
flowchart LR
    subgraph Request
        R1[conversationId: string]
        R2[message: string]
    end

    subgraph Response
        S1[conversationId]
        S2[answer: markdown]
        S3[sources: array]
        S4[toolsUsed: array]
        S5[facts: optional array]
        S6[recommendations: optional array]
        S7[debug: MCP/RAG/LLM provenance]
    end

    Request --> API[FastAPI handler]
    API --> Response

    classDef io fill:#E8EAF6,stroke:#3F51B5,color:#1A237E
    class Request,Response io
```

**Example request:**

```json
{
  "conversationId": "abc-123",
  "message": "Prepare me for my meeting with ACME"
}
```

**Example response (simplified):**

```json
{
  "conversationId": "abc-123",
  "answer": "ACME Executive Briefing\n\nFACT\nRevenue decreased 12%...",
  "sources": [
    { "title": "ACME Contract", "source": "contract-acme-2026.pdf" }
  ],
  "toolsUsed": ["get_customer", "get_customer_sales", "get_customer_tickets"],
  "debug": {
    "pipeline": ["mcp:get_customer", "mcp:get_customer_sales", "llm:synthesis"],
    "mcpCalls": [
      {
        "tool": "get_customer",
        "source": "mcp",
        "arguments": { "customer_id": "ACME-001" },
        "resultPreview": "{\"name\":\"ACME Corporation\"}",
        "durationMs": 12.3
      }
    ],
    "ragCalls": [],
    "llm": {
      "model": "gpt-4o-mini",
      "promptTokens": 1200,
      "completionTokens": 450,
      "note": "FACT bullets grounded in MCP/RAG; RECOMMENDATION is LLM-generated."
    }
  }
}
```

## Health checks

```mermaid
flowchart TD
    Probe[Load balancer / K8s probe] --> Health[GET /health]
    Probe --> Ready[GET /ready]

    Health --> H1{API process up?}
    H1 -->|yes| H200[200 OK]

    Ready --> R1{MCP reachable?}
    Ready --> R2{Azure deps OK? Phase 2+}
    R1 -->|all ok| R200[200 OK]
    R1 -->|fail| R503[503 — not ready]

    classDef ok fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    classDef fail fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    class H200,R200 ok
    class R503 fail
```

`/ready` **never** exposes connection strings or secrets — aggregated status only.

## Document ingestion (RAG pipeline)

Offline flow — command `python -m app.rag.ingest`:

```mermaid
flowchart TD
    Start([🚀 ingest command]) --> Load[📂 Load from Blob / data/]
    Load --> Extract[📄 Text extraction<br/>MD TXT PDF JSON]
    Extract --> Chunk[✂️ Chunking<br/>size=800 overlap=120]
    Chunk --> Meta[🏷️ Metadata extraction<br/>customer_id, document_type]
    Meta --> Embed[🧮 Embedding via Azure OpenAI]
    Embed --> Index[(📊 Azure AI Search index)]
    Index --> Done([✅ Done])

    classDef step fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    class Load,Extract,Chunk,Meta,Embed step
    class Index fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
```

## Telemetry per request (Phase 6)

Each execution produces a correlated trace:

```mermaid
flowchart TB
    Req[request_id] --> AgentExec[Agent execution 3.2s]
    AgentExec --> LLM1[LLM call #1 — 890ms]
    AgentExec --> MCPb[MCP batch — 450ms]
    AgentExec --> RAGs[RAG search — 220ms]
    AgentExec --> LLM2[LLM call #2 — 1.1s]
    MCPb --> T1[get_customer 120ms]
    MCPb --> T2[get_sales 180ms]
    RAGs --> Docs[5 documents retrieved]

    classDef trace fill:#FFF3E0,stroke:#E65100,color:#BF360C
    class AgentExec trace
```

See [observability.md](../observability.md) for details.

## Next step

→ [04 — Agent Decisions](04-agent-decisions.md)
