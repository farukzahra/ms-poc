# System Architecture

Consolidated architecture reference. Learning path: [`learn/`](learn/).

## Goals

1. **Enterprise agent** — not a generic chatbot
2. **Thin vertical slices** — Phase 1 runnable before Azure
3. **Separation of concerns** — HTTP ≠ Agent ≠ MCP ≠ RAG
4. **Grounded responses** — citations + FACT vs RECOMMENDATION
5. **Azure-ready** — path to Container Apps, Entra, Key Vault

## C4 — Context diagram

```mermaid
flowchart TB
    Rep[👤 Sales Representative] --> System[Enterprise AI Sales Intelligence]
    System --> CRM[CRM System]
    System --> Sales[Sales System]
    System --> Tickets[Support System]
    System --> Docs[Document Repository]
    System --> AzureAI[Azure AI Platform]

    classDef person fill:#FFE0B2,stroke:#E65100,color:#BF360C
    classDef system fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Rep person
    class System system
```

## C4 — Container diagram

```mermaid
flowchart TB
    subgraph Browser
        Web[Vue 3 SPA]
    end

    subgraph DockerLocal["Docker Compose — local"]
        API[FastAPI API]
        MCP[MCP Server]
        MCRM[mock-crm]
        MSales[mock-sales]
        MTkt[mock-tickets]
    end

    subgraph AzureCloud["Azure — Phase 2+"]
        OAI[Azure OpenAI]
        Search[AI Search]
        Blob[Blob Storage]
        ACA[Container Apps]
        Insights[App Insights]
    end

    Web -->|HTTPS JSON| API
    API --> MCP
    MCP --> MCRM
    MCP --> MSales
    MCP --> MTkt
    API --> OAI
    API --> Search
    Search --> Blob
    API --> Insights
    ACA --- API

    classDef container fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    class Web,API,MCP,MCRM,MSales,MTkt container
```

## Module dependencies (apps/api)

```mermaid
flowchart BT
    main[main.py] --> api[api/ routes]
    api --> agent[agent/]
    agent --> mcp_c[mcp/ client]
    agent --> rag[rag/]
    agent --> domain[domain/]
    rag --> infra[infrastructure/ azure clients]
    mcp_c --> infra
    api --> infra

    classDef mod fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    class agent,rag,mcp_c mod
```

**Dependency rule:** `domain/` has zero imports from `infrastructure/` or Azure SDKs.

## Production evolution (future)

```mermaid
flowchart TB
    Supervisor[Supervisor Agent] --> SalesA[Sales Agent]
    Supervisor --> SupportA[Support Agent]
    Supervisor --> ProductA[Product Agent]
    SalesA --> Data[Enterprise Data Layer]
    SupportA --> Data
    ProductA --> Data

    classDef future fill:#ECEFF1,stroke:#607D8B,color:#37474F
    class Supervisor,SalesA,SupportA,ProductA future
```

Not implemented in POC — documented for interview "From POC to Production".

## Related docs

- [mcp.md](mcp.md) — MCP server design
- [rag.md](rag.md) — RAG pipeline
- [security.md](security.md) — auth model
- [observability.md](observability.md) — telemetry
- [adrs/](adrs/) — decision records
