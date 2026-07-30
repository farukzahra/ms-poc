# 01 — Core Concepts

Before writing code, understand **what** we are building and **why** it is not a ordinary chatbot.

## Business problem

Enterprise sales reps need information scattered across many systems:

```mermaid
flowchart LR
    subgraph Sources["📂 Information sources"]
        CRM[(CRM)]
        Sales[(Sales)]
        Tickets[(Support)]
        Docs[(Policies & Docs)]
        Products[(Catalog)]
    end

    Rep[👤 Sales Rep] -->|30+ min| Sources

    classDef pain fill:#FFCDD2,stroke:#C62828,stroke-width:2px,color:#B71C1C
    class Rep pain
```

**POC goal:** reduce meeting prep to **under 5 minutes** with an agent that knows *where to fetch* each type of information.

## Chatbot vs enterprise agent

| | Generic chatbot | Sales Intelligence Agent |
|---|-----------------|--------------------------|
| Data source | Model only (parametric memory) | MCP (APIs) + RAG (documents) |
| Transactional data | Invents or stale | MCP → real REST APIs |
| Internal policies | Hallucinates | RAG → Azure AI Search |
| Tool selection | Fixed or none | Agent picks MCP / RAG / both |
| Citations | Optional | Required on RAG answers |
| Fact vs opinion | Mixed | UI separates FACT vs AI RECOMMENDATION |

```mermaid
flowchart TB
    subgraph Bad["❌ Anti-pattern"]
        U1[User] --> LLM1[LLM = everything]
    end

    subgraph Good["✅ Our architecture"]
        U2[User] --> AG[🧠 Agent]
        AG --> RAG[📚 RAG]
        AG --> MCP[🔌 MCP]
        RAG --> KB[(Knowledge Base)]
        MCP --> API[(Enterprise APIs)]
        AG --> LLM2[Azure OpenAI]
        LLM2 -.->|orchestrates| AG
    end

    classDef bad fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef good fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Bad bad
    class Good good
```

> **Golden rule:** the LLM **orchestrates**; it is not the company's knowledge base.

## RAG — Retrieval-Augmented Generation

**RAG** = retrieve relevant documents *before* generating the answer.

```mermaid
sequenceDiagram
    participant Q as User Query
    participant E as Embedding Model
    participant S as Azure AI Search
    participant L as Chat Model

    Q->>E: "enterprise AI deployment policy"
    E->>S: vector + keyword (hybrid)
    S-->>E: top-K chunks + metadata
    E->>L: prompt + retrieved context
    L-->>Q: grounded answer + citations
```

**When to use RAG:**

- Internal policies
- Product documentation
- Contracts (PDF/Markdown)
- Any knowledge that **changes** and is **not** in a structured API

**When NOT to use RAG:**

- "How much did ACME spend last year?" → transactional → **MCP**

## MCP — Model Context Protocol

**MCP** exposes enterprise capabilities as **tools** the agent invokes.

```mermaid
flowchart LR
    Agent[🧠 Agent] -->|MCP Client| MCP[MCP Server]
    MCP -->|HTTP REST| CRM[Mock CRM]
    MCP -->|HTTP REST| Sales[Mock Sales]
    MCP -->|HTTP REST| Tickets[Mock Tickets]

    classDef tool fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px,color:#4A148C
    class MCP tool
```

**Planned tools:**

| Tool | Source | Example use |
|------|--------|-------------|
| `get_customer` | CRM | ACME profile |
| `get_customer_sales` | Sales | Revenue, trend |
| `get_customer_tickets` | Tickets | Open issues |
| `get_customer_contracts` | Contracts | Renewal date |
| `search_products` | Products | Catalog |
| `get_product` | Products | Product detail |

**Why MCP instead of rewriting APIs for AI?**

```mermaid
flowchart TB
    REST[Existing REST APIs] -->|serve| Apps[Traditional apps]
    REST -->|same API| MCP[MCP Server]
    MCP -->|standard tools| Agent[AI Agent]

    classDef boundary fill:#BBDEFB,stroke:#1565C0,color:#0D47A1
    class MCP boundary
```

MCP is an **AI integration layer** — it does not duplicate business rules.

## Semantic Kernel — orchestration

**Semantic Kernel (SK)** is Microsoft's framework for:

- Plugging in LLM (Azure OpenAI)
- Registering plugins / functions
- Connecting MCP tools
- Keeping **prompts** and **orchestration** out of HTTP controllers

```mermaid
flowchart TB
    subgraph FastAPI["apps/api"]
        Routes[api/routes — thin HTTP]
        SK[agent/ — Semantic Kernel]
        Routes --> SK
    end

    SK --> MCPc[mcp/client]
    SK --> RAGs[rag/retriever]
    SK --> LLM[Azure OpenAI]

    classDef layer fill:#FFF3E0,stroke:#E65100,color:#BF360C
    class SK layer
```

## Grounding, citations, and responsible AI

| Concept | Meaning in this project |
|---------|-------------------------|
| **Grounding** | Answer based on retrieved evidence (RAG or API) |
| **Citation** | List real sources (`contract-acme.pdf`, `renewal-policy.md`) |
| **Hallucination** | Inventing customer data — **forbidden** |
| **Uncertainty** | "Insufficient evidence to claim X" |
| **FACT** | Data from MCP or cited document |
| **AI RECOMMENDATION** | Inferred suggestion — labeled in UI |

```mermaid
stateDiagram-v2
    [*] --> ReceiveQuestion
    ReceiveQuestion --> ClassifyIntent: Agent analyzes
    ClassifyIntent --> UseMCP: Transactional data
    ClassifyIntent --> UseRAG: Document knowledge
    ClassifyIntent --> UseBoth: Briefing / risks
    UseMCP --> Synthesize
    UseRAG --> Synthesize
    UseBoth --> Synthesize
    Synthesize --> LabelOutput: FACT vs RECOMMENDATION
    LabelOutput --> [*]
```

## Quick glossary

| Term | Short definition |
|------|------------------|
| **Embedding** | Numeric vector representing text meaning |
| **Hybrid search** | Keyword (BM25) + vector similarity |
| **Chunk** | Indexed document slice (e.g. 800 tokens, overlap 120) |
| **Top-K** | K most relevant documents/chunks returned |
| **Tool calling** | LLM selects and invokes external function (via MCP) |
| **Foundry** | Microsoft unified platform for Azure AI resources |

## Next step

→ [02 — Architecture Overview](02-architecture-overview.md)
