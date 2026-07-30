# ADR-004: RAG vs Structured API Access

## Status
Accepted

## Date
2026-07-30

## Context

The agent receives heterogeneous questions: transactional (revenue, ticket counts) and document-based (policies, contract clauses). Using RAG for everything causes wrong or stale answers; using APIs for everything misses unstructured knowledge.

## Decision

Enforce a **dual-path model**:

| Data type | Path |
|-----------|------|
| Transactional / structured | MCP → REST APIs |
| Document / policy / knowledge | RAG → Azure AI Search |
| Executive briefings / risk analysis | MCP + RAG combined |

Agent must classify intent before invoking tools.

## Alternatives Considered

### RAG-only (index everything including JSON exports)
- Pros: Single retrieval path
- Cons: Stale index, poor for live revenue; numeric answers need structured queries
- Rejected

### MCP-only (API-fy all documents)
- Pros: Always fresh if APIs updated
- Cons: Unrealistic for PDF policies; forces document parsing into CRM
- Rejected

### LLM memory / long context only
- Pros: Simple
- Cons: Hallucination, no citations, not enterprise-grade
- Rejected

## Consequences

- System prompt and eval dataset must reinforce routing rules
- Evaluation metrics include **tool selection accuracy**
- UI shows sources only when RAG contributed
- More agent complexity — acceptable for demo value
