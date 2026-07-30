# ADR-001: Use Semantic Kernel for Agent Orchestration

## Status
Accepted

## Date
2026-07-30

## Context

The POC requires an AI agent that:
- Calls MCP tools dynamically
- Invokes RAG retrieval
- Orchestrates multiple LLM turns (plan → execute → synthesize)
- Integrates with Microsoft Azure AI (OpenAI)

We need a framework that keeps orchestration **separate from FastAPI HTTP handlers**.

## Decision

Use **Semantic Kernel (Python)** as the primary agent orchestration layer in `apps/api/app/agent/`.

## Alternatives Considered

### LangChain / LangGraph
- Pros: Large ecosystem, many RAG examples
- Cons: Less aligned with Microsoft Solution Engineer interview narrative; SK is first-class in Azure AI stack
- Rejected for POC positioning

### Raw Azure OpenAI SDK only
- Pros: Minimal dependencies
- Cons: Manual tool loop, no plugin abstraction, more boilerplate for multi-step agents
- Rejected: orchestration complexity grows quickly

### AutoGen / CrewAI
- Pros: Multi-agent patterns
- Cons: Overkill for single-agent POC; harder to explain in 10-minute demo
- Rejected: YAGNI for Phase 1

## Consequences

- Agent logic lives in `agent/`, not in route handlers
- Prompts stored outside code (`prompts/sales-agent.system.md`)
- Team learns SK patterns applicable to Microsoft customer engagements
- Tight coupling to Microsoft ecosystem — acceptable for this POC
