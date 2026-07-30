# Enterprise AI deployment policy

All production AI workloads must register with the central AI governance board before deployment.

## Requirements

1. Models must run in approved Azure regions.
2. Customer data must not leave tenant boundaries without legal approval.
3. Retrieval systems must log document sources for audit.
4. Human review is required for customer-facing recommendations above risk tier 2.

## Approved patterns

- RAG over Azure AI Search with hybrid retrieval
- MCP tools for transactional enterprise APIs
- Semantic Kernel orchestration with Entra ID authentication
