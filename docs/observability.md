# Observability

Application Insights and AI-specific telemetry.

## Why observability matters for agents

> "Why did this agent response take 5 seconds?"

```mermaid
flowchart TB
    Q[Slow response] --> T[Trace request_id]
    T --> A[Agent execution span]
    A --> L1[LLM call 1 — planning]
    A --> M[MCP calls — 450ms]
    A --> R[RAG search — 220ms]
    A --> L2[LLM call 2 — synthesis]
    L1 --> Root[Identify bottleneck]

    classDef obs fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    class A,L1,M,R,L2 obs
```

## Correlation dimensions

| Field | Purpose |
|-------|---------|
| `request_id` | Single HTTP request |
| `conversation_id` | Multi-turn chat |
| `user_id` | Authenticated subject |
| `customer_id` | Business context (when authorized) |

## Agent execution trace (example)

```text
Agent Execution — 3.2s
├── LLM call #1 — 890ms (tool planning)
├── MCP get_customer — 120ms
├── MCP get_sales — 180ms
├── MCP get_tickets — 150ms
├── RAG search — 220ms (5 docs)
├── LLM call #2 — 1100ms (synthesis)
└── Tokens: in=2300 out=650
```

```mermaid
sequenceDiagram
    participant API as FastAPI
    participant AI as App Insights
    participant SK as Agent
    participant OAI as OpenAI
    participant MCP as MCP
    participant RAG as RAG

    API->>AI: start request span
    API->>SK: run_agent
    SK->>AI: span: llm_planning
    SK->>OAI: completion
    OAI-->>SK: tool calls
    SK->>AI: span: mcp_tools
    SK->>MCP: parallel tools
    MCP-->>SK: results
    SK->>AI: span: rag_search
    SK->>RAG: search
    RAG-->>SK: chunks
    SK->>AI: span: llm_synthesis
    SK->>OAI: completion
    SK-->>API: response
    API->>AI: end request span
```

## What to log

| Log | Include | Exclude |
|-----|---------|---------|
| Tool name | yes | — |
| Latency ms | yes | — |
| Token counts | yes | — |
| Retrieved doc titles | yes | full doc body |
| Customer PII | minimal IDs | emails, phones |

## Health vs readiness

| Endpoint | Checks |
|----------|--------|
| `/health` | Process alive |
| `/ready` | MCP reachable, Azure deps (Phase 2+) |

Never return connection strings in health responses.

## Phase introduction

| Phase | Telemetry |
|-------|-----------|
| 1 | Structured JSON logs to stdout |
| 6 | Application Insights + custom metrics |

Env: `APPLICATIONINSIGHTS_CONNECTION_STRING`
