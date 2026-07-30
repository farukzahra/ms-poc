# RAG — Retrieval-Augmented Generation

Deep dive on knowledge retrieval. Learning: [learn/01-concepts.md](learn/01-concepts.md), [learn/04-agent-decisions.md](learn/04-agent-decisions.md).

## Principle

```mermaid
flowchart LR
    LLM[LLM] -.->|does NOT store| Knowledge[(Company Knowledge)]
    Knowledge -->|indexed in| Search[(Azure AI Search)]
    Search -->|retrieved by| RAG[RAG Service]
    RAG -->|context to| LLM

    classDef ext fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Knowledge,Search,RAG ext
```

## KnowledgeRetriever interface

```python
class KnowledgeRetriever:
    async def search(
        self,
        query: str,
        customer_id: str | None = None,
    ) -> SearchResult:
        ...
```

## Search pipeline

```mermaid
flowchart TD
    Q[Query string] --> E[Generate embedding<br/>Azure OpenAI]
    E --> H[Hybrid search]
    H --> K[Keyword leg]
    H --> V[Vector leg]
    H --> F[Metadata filters<br/>customer_id document_type]
    F --> R[Semantic ranker]
    R --> K2[Top K chunks]
    K2 --> C[Build citations]

    classDef step fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    class E,H,R step
```

## Index schema — enterprise-knowledge

```mermaid
erDiagram
    DOCUMENT_CHUNK {
        string id PK
        string content
        string title
        string document_type
        string customer_id FK
        string department
        string source
        datetime created_at
        vector content_vector
    }
```

**Vector dimensions** must match embedding deployment — verify model, do not hardcode.

## Ingestion pipeline

Command: `python -m app.rag.ingest`

```mermaid
flowchart TD
    S1[📂 Source: Blob or data/] --> S2[Document loader]
    S2 --> S3{Format?}
    S3 -->|md txt| S4[Plain text]
    S3 -->|pdf| S5[PDF extractor]
    S3 -->|json| S6[JSON parser]
    S4 --> S7[Chunker CHUNK_SIZE OVERLAP]
    S5 --> S7
    S6 --> S7
    S7 --> S8[Metadata enrichment]
    S8 --> S9[Batch embed]
    S9 --> S10[Upsert AI Search]

    classDef pipe fill:#FFF9C4,stroke:#F9A825,color:#E65100
    class S2,S7,S9 pipe
```

### Chunking configuration

| Env var | Default | Effect |
|---------|---------|--------|
| `CHUNK_SIZE` | 800 | Larger → more context, less precision |
| `CHUNK_OVERLAP` | 120 | Overlap preserves sentence boundaries |

**Why overlap matters:** without it, facts split across chunk boundaries may never retrieve together.

## Citations contract

Every RAG-influenced answer must include:

```text
Sources:
- contract-acme-2026.pdf
- renewal-policy.md
```

```mermaid
flowchart LR
    Retrieve[Retrieved chunks] --> Cite[Map source field]
    Cite --> Response[API sources array]
    Response --> UI[Vue Sources panel]

    classDef cite fill:#E8F5E9,stroke:#388E3C,color:#1B5E20
    class Cite,UI cite
```

**Never cite a source not in retrieved set** — hallucinated citations fail evaluation.

## When NOT to use RAG

| Question type | Use instead |
|---------------|-------------|
| Revenue, spend, counts | MCP → Sales API |
| Customer profile fields | MCP → CRM |
| Open ticket count | MCP → Tickets API |

See decision matrix in [learn/04-agent-decisions.md](learn/04-agent-decisions.md).

## Cost optimizations

- Cache embeddings for unchanged documents
- Small embedding model (`text-embedding-3-small`)
- Limit Top-K (e.g. 5 chunks)
- Small demo dataset

See [cost.md](cost.md).

## ADR

[ADR-003: Why Azure AI Search](adrs/ADR-003-azure-ai-search.md), [ADR-004: RAG vs API](adrs/ADR-004-rag-vs-structured-api.md).
