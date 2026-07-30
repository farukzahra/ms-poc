# ADR-006: Agent Security Model

## Status
Accepted

## Date
2026-07-30

## Context

Sales intelligence exposes sensitive customer data. The chat UI will mention customer names (ACME) but authorization must prevent cross-customer data leakage.

## Decision

1. **Production auth:** Microsoft Entra ID JWT on all `/api/v1/*` routes (Phase 6)
2. **Authorization:** Backend derives permitted `customer_id` set from authenticated identity — never trust frontend-only customer selection
3. **Roles:** `SALES_REP`, `SALES_MANAGER`, `ADMIN`
4. **Secrets:** Key Vault in Azure; `.env` local only
5. **Dev bypass:** `DEV_AUTH_ENABLED` for Phase 1 local only — documented and disabled in deploy

## Alternatives Considered

### API key only
- Pros: Simple
- Cons: No user identity, no RBAC, weak enterprise story
- Rejected for production path

### Customer ID in request body without auth
- Pros: Fastest POC
- Cons: Trivial data exfiltration
- Rejected — unacceptable even for demo deploy

### Session cookie custom auth
- Pros: Full control
- Cons: Reinvents Entra; bad for Microsoft interview
- Rejected

## Consequences

- Phase 1 uses mock auth with clear warnings
- MCP tools receive only authorized customer IDs from agent layer
- Telemetry redacts PII where possible
- Entra setup deferred to Phase 6 but ADR documents target state early
