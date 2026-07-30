# 05 — Azure Services

Mapa de cada serviço Azure no projeto — **o que faz**, **quando entra**, **como se conecta**.

## Mapa de serviços

```mermaid
flowchart TB
    subgraph RG["Resource Group: rg-ai-sales-poc"]
        OAI[🔮 Azure OpenAI / Foundry<br/>chat + embeddings]
        Search[(🔍 Azure AI Search<br/>enterprise-knowledge)]
        Blob[(📦 Blob Storage<br/>documents/)]
        ACA[⚙️ Container Apps<br/>FastAPI API]
        KV[🔐 Key Vault<br/>secrets]
        AI[📊 Application Insights<br/>telemetry]
        Entra[🎫 Microsoft Entra ID<br/>auth]
    end

    User[👤 User] --> ACA
    ACA --> OAI
    ACA --> Search
    ACA --> KV
    ACA --> AI
    Entra --> ACA
    Search --> Blob
    Ingest[ingest pipeline] --> Blob
    Ingest --> OAI
    Ingest --> Search

    classDef svc fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    class OAI,Search,Blob,ACA,KV,AI,Entra svc
```

## Fase de introdução

| Serviço | Phase | Por quê esperar |
|---------|-------|-----------------|
| Mock APIs + Docker | 1 | Provar arquitetura sem custo |
| Azure OpenAI | 2 | LLM real, tool calling |
| Azure AI Search | 3 | RAG, hybrid search |
| Blob Storage | 4 | Fonte canonica de docs |
| Container Apps | 5 | Deploy managed |
| Entra + Key Vault + Insights | 6 | Security + observability |

## Azure OpenAI / Microsoft Foundry

**Papel:** inferência LLM + embeddings.

```mermaid
flowchart LR
    subgraph Deployments
        Chat[gpt-4o-mini<br/>AZURE_CHAT_DEPLOYMENT]
        Emb[text-embedding-3-small<br/>AZURE_EMBEDDING_DEPLOYMENT]
    end

    Agent[Agent] -->|chat completions| Chat
    RAG[RAG] -->|embed query + docs| Emb
    Chat --> Agent
    Emb --> RAG

    classDef model fill:#F3E5F5,stroke:#7B1FA2,color:#4A148C
    class Chat,Emb model
```

**Env vars** (ver `.env.example`):

```env
AZURE_AI_ENDPOINT=
AZURE_AI_API_KEY=
AZURE_CHAT_DEPLOYMENT=
AZURE_EMBEDDING_DEPLOYMENT=
```

**Regras:**

- Modelos configuráveis — não hardcodar API version deprecated
- Modelos **pequenos** para POC (custo)
- Não commitar keys — Key Vault em produção

## Azure AI Search

**Papel:** retrieval layer — **não** é o LLM.

**Index `enterprise-knowledge`:**

| Field | Type | Uso |
|-------|------|-----|
| `id` | string | PK |
| `content` | string | Texto do chunk |
| `title` | string | Título documento |
| `document_type` | string | policy, contract, product |
| `customer_id` | string | Filtro ACME-001 |
| `department` | string | Filtro org |
| `source` | string | Nome arquivo origem |
| `created_at` | datetime | Ordenação |
| `content_vector` | vector | Dim = embedding model |

```mermaid
flowchart TD
    Query[User query] --> Embed[Embedding]
    Embed --> Hybrid[Hybrid Search]
    Hybrid --> KW[Keyword BM25]
    Hybrid --> Vec[Vector similarity]
    Hybrid --> Filter[Metadata filter<br/>customer_id=ACME-001]
    Filter --> Rank[Semantic ranking]
    Rank --> TopK[Top K chunks]

    classDef search fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    class Hybrid,Rank search
```

## Azure Blob Storage

Estrutura de pastas:

```text
documents/
  customers/
  products/
  contracts/
  policies/
  sales/
```

```mermaid
flowchart LR
    Upload[Sample files in data/] -->|ingest| Blob[(Blob)]
    Blob -->|loader| Pipeline[Ingestion pipeline]
    Pipeline --> Search[(AI Search index)]
```

**Phase 4:** Blob vira source of truth; local `data/` espelha para dev.

## Azure Container Apps

**Papel:** hospedar FastAPI sem gerenciar Kubernetes.

```mermaid
flowchart TB
    subgraph ACA["Container App"]
        C1[Container: ms-poc-api]
        C1 --> Port[Port 8000]
        C1 --> Env[Env from Key Vault refs]
    end

    Ingress[HTTPS Ingress] --> ACA
    ACA --> Health[/health /ready]

    classDef container fill:#FFF3E0,stroke:#E65100,color:#BF360C
    class C1 container
```

Requisitos container:

- Listen on configured port
- Structured logs → App Insights
- No local persistent storage
- Env vars only (no secrets in image)

## Microsoft Entra ID

**Phase 6** — autenticação enterprise.

```mermaid
sequenceDiagram
    participant U as User
    participant Vue as Vue App
    participant Entra as Entra ID
    participant API as FastAPI

    U->>Vue: Login
    Vue->>Entra: OAuth2 / OIDC
    Entra-->>Vue: JWT access token
    Vue->>API: Authorization: Bearer JWT
    API->>API: validate token + roles
    API-->>Vue: authorized response
```

**Roles:** `SALES_REP`, `SALES_MANAGER`, `ADMIN`

## Application Insights

Correlaciona: `request_id`, `conversation_id`, latências LLM/MCP/RAG, token usage.

Ver [observability.md](../observability.md).

## Budget e região

| Config | Valor POC |
|--------|-----------|
| Resource group | `rg-ai-sales-poc` |
| Region | `eastus` (consistente) |
| Budget alert | ~$50 com alertas 50/75/90/100% |

Detalhes: [cost.md](../cost.md).

## Azure CLI — comandos essenciais

```bash
az login
az account show
az group create --name rg-ai-sales-poc --location eastus
az deployment group create --resource-group rg-ai-sales-poc --template-file infrastructure/azure/bicep/main.bicep
```

Nunca hardcodar subscription ID — usar:

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
```

## Próximo passo

→ [06 — Demo Scenarios](06-demo-scenarios.md)
