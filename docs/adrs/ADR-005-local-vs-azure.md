# ADR-005: Local Development Before Azure Resources

## Status
Accepted

## Date
2026-07-30

## Context

Developer has Azure free account ($200 / 30 days) but credits should not be consumed during initial architecture work. PLAN mandates phased delivery.

## Decision

Implement **Phase 1 entirely local**:
- Docker Compose for Vue, FastAPI, MCP, mock APIs
- Mock or stub LLM until Phase 2
- No Azure resources until OpenAI integration is ready to test

Phases 2–6 introduce Azure services incrementally.

## Alternatives Considered

### Create all Azure resources on day 1
- Pros: No migration surprises
- Cons: Burns credits during scaffolding; violates PLAN cost strategy
- Rejected

### Cloud-only development
- Pros: Production parity
- Cons: Slower iteration, costs during debug
- Rejected

## Consequences

- `docker compose up` is the primary dev entry point for weeks 1–2
- Must not claim Azure integration works until tested against real services
- `.env.example` documents Azure vars early but they stay empty in Phase 1
- Clear interview story: "iterate locally, integrate Azure when ready"
