# MCP — Model Context Protocol

Deep dive on the MCP layer. Learning guide: [learn/01-concepts.md](learn/01-concepts.md).

## Role in architecture

MCP is the **AI integration boundary** between the agent and existing REST APIs.

```mermaid
flowchart LR
    Agent[Semantic Kernel Agent] -->|MCP Client| Server[MCP Server :8001]
    Server -->|httpx REST| CRM[CRM :8101]
    Server -->|httpx REST| Sales[Sales :8102]
    Server -->|httpx REST| Tickets[Tickets :8103]
    Server --> Contracts[Contracts :8104]
    Server --> Products[Products :8105]

    classDef mcp fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px,color:#4A148C
    class Server mcp
```

## Transport — streamable-http

Project decision: **HTTP** (not stdio) for Docker Compose networking.

```mermaid
sequenceDiagram
    participant Client as MCP Client in API
    participant Server as MCP Server :8001
    participant API as Mock REST

    Client->>Server: HTTP MCP protocol
    Server->>API: GET /customers/{id}
    API-->>Server: JSON
    Server-->>Client: tool result
```

Env: `MCP_SERVER_URL=http://localhost:8001`

## Tool catalog

| Tool | REST mapping | Returns |
|------|--------------|---------|
| `get_customer` | `GET /customers/{id}` | Profile, segment |
| `get_customer_sales` | `GET /customers/{id}/sales` | Revenue, transactions |
| `get_customer_tickets` | `GET /customers/{id}/tickets` | Open/closed issues |
| `get_customer_contracts` | `GET /customers/{id}/contracts` | Renewal, terms |
| `search_products` | `GET /products?q=` | Product list |
| `get_product` | `GET /products/{id}` | Product detail |

## MCP server structure

```mermaid
flowchart TB
    subgraph apps/mcp-server
        Entry[server/main.py FastMCP]
        Tools[tools/ @mcp.tool]
        Clients[clients/ httpx async]
    end

    Entry --> Tools
    Tools --> Clients
    Clients --> Env[CRM_API_URL SALES_API_URL]

    classDef internal fill:#FFF3E0,stroke:#E65100,color:#BF360C
    class Entry,Tools,Clients internal
```

## Design rules

| Rule | Rationale |
|------|-----------|
| No business logic duplication | REST APIs remain source of truth |
| Typed tool inputs/outputs | Pydantic models for LLM schema |
| Async I/O | Parallel tool calls via httpx |
| Error mapping | HTTP errors to structured tool errors |
| No secrets in responses | Never leak keys or internal URLs |

## Parallel tool execution

```mermaid
flowchart TB
    Agent[Agent planner] --> P[asyncio.gather]
    P --> T1[get_customer]
    P --> T2[get_customer_sales]
    P --> T3[get_customer_tickets]
    T1 --> Merge[Merge results]
    T2 --> Merge
    T3 --> Merge
    Merge --> LLM[Synthesis LLM call]
```

## ADR

See [ADR-002: Why MCP](adrs/ADR-002-mcp.md).
