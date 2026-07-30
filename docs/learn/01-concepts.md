# 01 — Core Concepts

Antes de escrever código, entenda **o que** estamos construindo e **por que** não é um chatbot comum.

## O problema de negócio

Vendedores enterprise precisam de informação espalhada em vários sistemas:

```mermaid
flowchart LR
    subgraph Sources["📂 Fontes de informação"]
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

**Objetivo da POC:** reduzir essa preparação para **menos de 5 minutos** com um agente que sabe *onde buscar* cada tipo de informação.

## Chatbot vs Enterprise Agent

| | Chatbot genérico | Sales Intelligence Agent |
|---|------------------|--------------------------|
| Fonte de dados | Só o modelo (memória paramétrica) | MCP (APIs) + RAG (documentos) |
| Dados transacionais | Inventa ou desatualiza | MCP → REST APIs reais |
| Políticas internas | Alucina | RAG → Azure AI Search |
| Decisão de ferramenta | Fixa ou inexistente | Agent decide MCP / RAG / both |
| Citações | Opcionais | Obrigatórias em respostas RAG |
| Fato vs opinião | Misturado | UI separa FACT vs AI RECOMMENDATION |

```mermaid
flowchart TB
    subgraph Bad["❌ Anti-pattern"]
        U1[User] --> LLM1[LLM = everything]
    end

    subgraph Good["✅ Nossa arquitetura"]
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

> **Regra de ouro:** o LLM **orquestra**; não é a base de conhecimento da empresa.

## RAG — Retrieval-Augmented Generation

**RAG** = buscar documentos relevantes *antes* de gerar a resposta.

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

**Quando usar RAG:**

- Políticas internas
- Documentação de produto
- Contratos em PDF/Markdown
- Qualquer conhecimento que **muda** e **não** está em API estruturada

**Quando NÃO usar RAG:**

- "Quanto ACME gastou ano passado?" → dado transacional → **MCP**

## MCP — Model Context Protocol

**MCP** expõe capacidades enterprise como **tools** que o agent invoca.

```mermaid
flowchart LR
    Agent[🧠 Agent] -->|MCP Client| MCP[MCP Server]
    MCP -->|HTTP REST| CRM[Mock CRM]
    MCP -->|HTTP REST| Sales[Mock Sales]
    MCP -->|HTTP REST| Tickets[Mock Tickets]

    classDef tool fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px,color:#4A148C
    class MCP tool
```

**Tools planejadas:**

| Tool | Fonte | Exemplo de uso |
|------|-------|----------------|
| `get_customer` | CRM | Perfil ACME |
| `get_customer_sales` | Sales | Receita, tendência |
| `get_customer_tickets` | Tickets | Issues abertas |
| `get_customer_contracts` | Contracts | Renewal date |
| `search_products` | Products | Catálogo |
| `get_product` | Products | Detalhe produto |

**Por que MCP e não reescrever APIs para AI?**

```mermaid
flowchart TB
    REST[REST APIs existentes] -->|servem| Apps[Apps tradicionais]
    REST -->|mesma API| MCP[MCP Server]
    MCP -->|tools padronizadas| Agent[AI Agent]

    classDef boundary fill:#BBDEFB,stroke:#1565C0,color:#0D47A1
    class MCP boundary
```

O MCP é uma **camada de integração AI** — não duplica regra de negócio.

## Semantic Kernel — Orquestração

**Semantic Kernel (SK)** é o framework Microsoft para:

- Pluggar LLM (Azure OpenAI)
- Registrar plugins / functions
- Conectar MCP tools
- Manter **prompts** e **orchestration** fora dos controllers HTTP

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

## Grounding, citations e responsible AI

| Conceito | Significado neste projeto |
|----------|---------------------------|
| **Grounding** | Resposta baseada em evidência recuperada (RAG ou API) |
| **Citation** | Listar fontes reais (`contract-acme.pdf`, `renewal-policy.md`) |
| **Hallucination** | Inventar dado de cliente — **proibido** |
| **Uncertainty** | "Não há evidência suficiente para afirmar X" |
| **FACT** | Dado vindo de MCP ou documento citado |
| **AI RECOMMENDATION** | Sugestão inferida — rotulada na UI |

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

## Glossário rápido

| Termo | Definição curta |
|-------|-----------------|
| **Embedding** | Vetor numérico que representa significado de texto |
| **Hybrid search** | Keyword (BM25) + vector similarity |
| **Chunk** | Pedaço de documento indexado (ex.: 800 tokens, overlap 120) |
| **Top-K** | K documentos/chunks mais relevantes retornados |
| **Tool calling** | LLM escolhe e invoca função externa (via MCP) |
| **Foundry** | Plataforma Microsoft unificada para recursos AI no Azure |

## Próximo passo

→ [02 — Architecture Overview](02-architecture-overview.md)
