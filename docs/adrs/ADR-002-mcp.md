# ADR-002: Use MCP for Enterprise Tool Integration

## Status
Accepted

## Date
2026-07-30

## Context

The agent must access CRM, Sales, Tickets, Contracts, and Products. These systems already expose (or will expose) **REST APIs**. We need a standardized way for the LLM to invoke enterprise capabilities without rewriting backends for AI.

## Decision

Expose enterprise REST APIs through a dedicated **MCP Server** (`apps/mcp-server/`) using **streamable-http** transport on port **8001**.

## Alternatives Considered

### Direct REST calls from agent code
- Pros: Fewer moving parts
- Cons: No standard tool schema; harder to swap implementations; mixes integration with orchestration
- Rejected

### OpenAPI → function calling code generation
- Pros: Auto-generated bindings
- Cons: Not a portable standard across agents/tools; interview story weaker
- Rejected for POC narrative

### MCP stdio transport
- Pros: Simple local subprocess model
- Cons: Poor fit for Docker Compose multi-container setup
- Rejected — use HTTP per project decision

## Consequences

- Clear boundary: `REST → MCP Server → MCP Client → Agent`
- MCP server contains **no duplicated business logic** — only HTTP forwarding + typing
- Tools are discoverable and testable independently
- Additional container in Docker Compose
