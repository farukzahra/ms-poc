# 02 — Architecture Overview

Structural view of the monorepo, layers, and deployment.

## High-level diagram

```mermaid
flowchart TB
    subgraph UserLayer["👤 User Layer"]
        Rep[Sales Rep Browser]
    end

    subgraph Frontend["apps/web — Vue 3 + Vite"]
        Chat[Chat UI]
        Sources[Sources Panel]
        Facts[FACT / RECOMMENDATION]
    end

    subgraph Backend["apps/api — Python FastAPI"]
        API[api/v1/chat]
        Health[/health /ready]
        Agent[agent/ Semantic Kernel]
        RAGm[rag/ KnowledgeRetriever]
        MCPc[mcp/ Client]
    end

    subgraph MCPLayer["apps/mcp-server"]
        MCPS[MCP Server streamable-http]
        Tools[get_customer, get_sales, ...]
    end

    subgraph Mocks["services/ — Docker local"]
        CRM[mock-crm :8101]
        Sales[mock-sales :8102]
        Tkt[mock-tickets :8103]
    end

    subgraph Azure["☁️ Azure (Phase 2+)"]
        OAI[Azure OpenAI / Foundry]
        Search[(Azure AI Search)]
        Blob[(Blob Storage)]
        ACA[Container Apps]
        Insights[Application Insights]
        Entra[Microsoft Entra ID]
    end

    Rep --> Chat
    Chat -->|POST /api/v1/chat| API
    API --> Agent
    Agent --> MCPc
    Agent --> RAGm
    Agent --> OAI
    MCPc -->|HTTP| MCPS
    MCPS --> Tools
    Tools --> CRM
    Tools --> Sales
    Tools --> Tkt
    RAGm --> Search
    Search --> Blob
    API --> Insights
    API --> ACA
    Entra -.->|JWT Phase 6| API

    classDef azure fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef local fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#4A148C
    class Azure azure
    class Mocks,MCPLayer local
```

## Monorepo — estrutura de pastas

```mermaid
flowchart TD
    Root[ms-poc/]
    Root --> Apps[apps/]
    Root --> Svc[services/]
    Root --> Data[data/]
    Root --> Infra[infrastructure/azure/]
    Root --> Docs[docs/]

    Apps --> Api[api/]
    Apps --> McpApp[mcp-server/]
    Apps --> Web[web/]

    Api --> ApiApp[app/api agent rag mcp domain infrastructure]
    Api --> ApiTests[tests/]

    Svc --> MockCRM[mock-crm/]
    Svc --> MockSales[mock-sales/]
    Svc --> MockTkt[mock-tickets/]

    Data --> Customers[customers/]
    Data --> Products[products/]
    Data --> Policies[policies/]

    classDef folder fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    class Apps,Svc,Data,Infra,Docs folder
```

## Layers and responsibilities

| Layer | Folder | Responsibility | Must not |
|-------|--------|----------------|----------|
| **HTTP** | `apps/api/app/api/` | Validate request, auth, serialize response | Contain agent logic |
| **Agent** | `apps/api/app/agent/` | Intent, tool selection, synthesis | Call mock HTTP directly |
| **RAG** | `apps/api/app/rag/` | Embed, search, filter, rank | Invent content |
| **MCP client** | `apps/api/app/mcp/` | Connect to MCP server | Duplicate tools |
| **MCP server** | `apps/mcp-server/` | Expose tools, call REST | Duplicate business rules |
| **Domain** | `apps/api/app/domain/` | Types, DTOs, enums | Azure dependencies |
| **Infrastructure** | `apps/api/app/infrastructure/` | Azure clients, telemetry | Business logic |
| **UI** | `apps/web/src/` | Chat, sources, loading | Authorize by customer_id alone |

## Deployment — local vs Azure

```mermaid
flowchart LR
    subgraph Local["🐳 docker compose up"]
        direction TB
        L1[Vue :5173]
        L2[FastAPI :8000]
        L3[MCP :8001]
        L4[Mocks :810x]
    end

    subgraph Cloud["☁️ Azure Phase 5+"]
        direction TB
        C1[Container Apps — API]
        C2[Static Web / Container — Vue]
        C3[Azure OpenAI]
        C4[AI Search + Blob]
        C5[App Insights + Entra]
    end

    Local -.->|Phase 2+ connect| Cloud

    classDef docker fill:#FFF9C4,stroke:#F9A825,color:#F57F17
    classDef cloud fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    class Local docker
    class Cloud cloud
```

## Default local ports

| Service | Port | Health endpoint |
|---------|------|-----------------|
| Vue | 5173 | home page |
| FastAPI | 8000 | `GET /health`, `GET /ready` |
| MCP Server | 8001 | per transport |
| Mock CRM | 8101 | `GET /health` |
| Mock Sales | 8102 | `GET /health` |
| Mock Tickets | 8103 | `GET /health` |

## Principle: LLM ↔ retrieval separation

```mermaid
flowchart TB
    subgraph Wrong["LLM as database"]
        Q1[Question] --> M1[Model memory]
        M1 --> A1[Maybe wrong answer]
    end

    subgraph Right["External knowledge"]
        Q2[Question] --> R[Retriever]
        R --> D[(Documents + APIs)]
        D --> P[Prompt + evidence]
        P --> M2[Model]
        M2 --> A2[Grounded answer]
    end

    classDef wrong fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef right fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Wrong wrong
    class Right right
```

## Dataset demo — ACME Corporation

Fictional data with intentional relationships for agent reasoning:

```mermaid
erDiagram
    CUSTOMER ||--o{ SALE : has
    CUSTOMER ||--o{ TICKET : opens
    CUSTOMER ||--o{ CONTRACT : signs
    CUSTOMER }o--o{ PRODUCT : uses
    POLICY ||--o{ DOCUMENT : governs

    CUSTOMER {
        string id PK "ACME-001"
        string name "ACME Corporation"
        float revenue_trend "-12%"
    }
    CONTRACT {
        string id PK
        int renewal_days "74"
    }
    TICKET {
        string id PK
        string status "open"
    }
```

## Next step

→ [03 — Request Flow](03-request-flow.md)
