# Security

Auth, authorization, and secrets for the Sales Intelligence POC.

## Threat model (POC scope)

```mermaid
flowchart TB
    subgraph Threats
        T1[Unauthorized customer data access]
        T2[Secret leakage in git/logs]
        T3[Frontend spoofed customer_id]
        T4[PII in telemetry]
    end

    subgraph Mitigations
        M1[Entra ID JWT Phase 6]
        M2[Key Vault + gitignore]
        M3[Backend auth from identity]
        M4[Redact sensitive fields in logs]
    end

    T1 --> M1
    T2 --> M2
    T3 --> M3
    T4 --> M4

    classDef threat fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef mit fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Threats threat
    class Mitigations mit
```

## Authentication flow (production target)

```mermaid
sequenceDiagram
    participant U as User
    participant Vue as Vue App
    participant Entra as Microsoft Entra ID
    participant API as FastAPI

    U->>Vue: Login
    Vue->>Entra: OIDC authorization code
    Entra-->>Vue: access_token JWT
    Vue->>API: Bearer token
    API->>API: Validate JWT signature + audience
    API->>API: Extract roles + user_id
    API-->>Vue: Authorized response
```

## Roles

| Role | Capabilities |
|------|--------------|
| `SALES_REP` | Own accounts, chat, briefings |
| `SALES_MANAGER` | Team accounts + reports |
| `ADMIN` | Full access, config |

## Authorization rule — critical

```mermaid
flowchart LR
    subgraph Wrong
        FE[Frontend sends customer_id] --> API1[API trusts it]
    end

    subgraph Correct
        JWT[JWT identity] --> API2[Resolve allowed customers]
        API2 --> MCP[MCP calls for authorized IDs only]
    end

    classDef wrong fill:#FFCDD2,stroke:#C62828,color:#B71C1C
    classDef right fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class Wrong wrong
    class Correct right
```

**Never authorize using only `customer_id` from the frontend.**

## Phase 1 — local dev auth

Until Entra is wired:

- `DEV_AUTH_ENABLED=true` in `.env` (local only)
- Mock user with fixed role for development
- Document clearly — **not for production**

## Secrets management

| Environment | Storage |
|-------------|---------|
| Local | `.env` (gitignored) |
| Azure | Key Vault references in Container Apps |
| CI/CD | GitHub Secrets (future) |

**Never commit:** API keys, passwords, tokens, client secrets, connection strings with keys.

See root [`.gitignore`](../.gitignore).

## Production security evolution

Documented for interview — not all implemented in POC:

- Managed Identity (no keys in app)
- Private Endpoints for Search/OpenAI
- VNet integration for Container Apps
- Azure Policy + Defender for Cloud
- RBAC on Search index by department

See [PLAN.md §45](PLAN.md#45-security-evolution).

## ADR

[ADR-006: Agent security model](adrs/ADR-006-agent-security.md).
