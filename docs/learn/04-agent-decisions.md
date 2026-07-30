# 04 — Agent Decisions: MCP vs RAG

O diferencial desta POC é o agent **decidir** qual capacidade usar — não chamar tudo sempre.

## Árvore de decisão

```mermaid
flowchart TD
    Q[User question] --> A{Agent classifies intent}

    A -->|Transactional numeric/factual| MCPonly[MCP only]
    A -->|Policy / documentation| RAGonly[RAG only]
    A -->|Briefing / risk / recommendation| Both[MCP + RAG]
    A -->|General chat outside scope| Refuse[Decline — insufficient scope]

    MCPonly --> Ex1["How much did ACME spend?"]
    RAGonly --> Ex2["Enterprise AI deployment policy?"]
    Both --> Ex3["Prepare ACME meeting / renewal risks?"]

    classDef mcp fill:#E1BEE7,stroke:#6A1B9A,color:#4A148C
    classDef rag fill:#BBDEFB,stroke:#1565C0,color:#0D47A1
    classDef both fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class MCPonly,Ex1 mcp
    class RAGonly,Ex2 rag
    class Both,Ex3 both
```

## Matriz de cenários demo

| # | Pergunta | MCP | RAG | Reasoning |
|---|----------|-----|-----|-----------|
| 1 | Prepare me for my meeting with ACME | ✅ | ✅ | Briefing = dados + docs |
| 2 | How much did ACME spend last year? | ✅ | ❌ | Número em Sales API |
| 3 | What is our enterprise AI deployment policy? | ❌ | ✅ | Política em documento |
| 4 | What products should we recommend to ACME? | ✅ | ✅ | Catálogo + histórico + docs |
| 5 | Biggest risks to ACME's renewal? | ✅ | ✅ | Tickets + contract + policy |

## Fluxo por cenário

### Cenário 2 — MCP only

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant M as MCP
    participant S as Sales API

    U->>A: How much did ACME spend last year?
    A->>A: intent = transactional → MCP
    A->>M: get_customer_sales(ACME-001)
    M->>S: GET /customers/ACME-001/sales
    S-->>M: $2.4M annual
    M-->>A: structured JSON
    A-->>U: FACT: ACME spent $2.4M last year
    Note over A: No RAG call — avoids wrong doc snippets
```

### Cenário 3 — RAG only

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant R as RAG
    participant I as AI Search

    U->>A: Enterprise AI deployment policy?
    A->>A: intent = organizational knowledge → RAG
    A->>R: search("enterprise AI deployment policy")
    R->>I: hybrid search, filter document_type=policy
    I-->>R: ai-deployment-policy.md chunks
    R-->>A: context + citations
    A-->>U: Answer + Sources list
    Note over A: No MCP — CRM irrelevant
```

### Cenário 5 — MCP + RAG + reasoning

```mermaid
flowchart TB
    Q[Renewal risks for ACME?] --> Gather

    subgraph Gather["Evidence gathering"]
        MCP1[get_customer_sales → -12% trend]
        MCP2[get_customer_tickets → 3 open]
        MCP3[get_customer_contracts → 74 days renewal]
        RAG1[search renewal policy + contract terms]
    end

    Gather --> Reason[LLM synthesize risks]
    Reason --> Out[FACT blocks + AI RECOMMENDATION blocks]

    classDef fact fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    classDef rec fill:#FFF9C4,stroke:#F9A825,color:#E65100
    class MCP1,MCP2,MCP3,RAG1 fact
    class Out rec
```

## System prompt — regras que guiam decisões

O prompt vive **fora** do código (`prompts/sales-agent.system.md`):

| Regra | Efeito na decisão |
|-------|-------------------|
| Never invent customer data | Prefere MCP para facts |
| Prefer structured systems for transactional info | Sales/revenue → MCP |
| Use RAG for organizational knowledge | Policies → RAG |
| Use both when necessary | Briefings |
| Cite retrieved documents | RAG responses only |
| If evidence insufficient, say so | No guessing |

## Anti-patterns a evitar

```mermaid
flowchart LR
    subgraph Bad
        B1[Always call all tools]
        B2[Use RAG for revenue numbers]
        B3[Trust customer_id from frontend]
        B4[Skip citations when RAG used]
    end

    subgraph Good
        G1[Minimal tools for intent]
        G2[MCP for structured data]
        G3[Auth-derived customer access]
        G4[Sources panel always for RAG]
    end

    classDef bad fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef good fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Bad bad
    class Good good
```

## Evaluation — medir tool selection

Dataset em `data/eval/tool-selection.json`:

```json
{
  "question": "How much did ACME spend last year?",
  "expectedTool": "get_customer_sales",
  "expectedSource": null
}
```

```json
{
  "question": "What is our enterprise AI deployment policy?",
  "expectedTool": null,
  "expectedSource": "RAG"
}
```

Métricas: tool selection accuracy, grounding rate, citation accuracy — ver [llm-evaluation skill](../../.agents/skills/llm-evaluation/SKILL.md).

## Próximo passo

→ [05 — Azure Services](05-azure-services.md)
