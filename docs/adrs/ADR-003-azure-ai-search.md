# ADR-003: Use Azure AI Search for Enterprise Retrieval

## Status
Accepted

## Date
2026-07-30

## Context

Enterprise knowledge (policies, contracts, product docs) changes frequently and must **not** live inside LLM weights. Requirements:
- Vector search
- Keyword search
- Hybrid search
- Metadata filtering (`customer_id`, `document_type`)
- Semantic ranking
- Scalable indexing

## Decision

Use **Azure AI Search** with index `enterprise-knowledge` as the sole retrieval store for RAG.

## Alternatives Considered

### PostgreSQL + pgvector
- Pros: Single database, familiar SQL
- Cons: Weaker hybrid/semantic ranking story for Microsoft interview; not Azure-native AI Search
- Rejected for POC positioning

### Chroma / local vector DB
- Pros: Free local dev
- Cons: No production path on Azure; different API in prod
- Rejected — prefer Azure Search from Phase 3 even if heavier setup

### Cosmos DB vector
- Pros: Azure native
- Cons: Less mature hybrid search narrative vs AI Search for document retrieval
- Rejected

## Consequences

- Ingestion pipeline targets AI Search index
- Embedding dimensions must match deployed embedding model
- Cost: Search SKU is a major budget item — use Basic tier
- Excellent alignment with "AI & Apps Solution Engineer" demo
