# 06 — Demo Scenarios

The **5 scenarios** that prove value in the 10-minute demo and interview.

## Demo overview (10 min)

```mermaid
flowchart LR
    D1[1. Business problem] --> D2[2. Architecture]
    D2 --> D3[3. ACME briefing]
    D3 --> D4[4. Structured MCP]
    D4 --> D5[5. RAG policy]
    D5 --> D6[6. Combined risks]
    D6 --> D7[7. Observability]
    D7 --> D8[8. Production evolution]

    classDef demo fill:#E1F5FE,stroke:#0277BD,color:#01579B
    class D1,D2,D3,D4,D5,D6,D7,D8 demo
```

## Dataset — ACME Corporation

| Attribute | Demo value | Why it matters |
|----------|------------|-----------------|
| Revenue trend | -12% QoQ | Risk signal |
| Open tickets | 3 | Support risk |
| Renewal | 74 days | Urgency |
| Products | Analytics + Enterprise Platform | Upsell context |
| Opportunity | Enterprise AI Automation | Talking point |

Additional customers: **Globex**, **Initech** — same structure, different relationships.

## Scenario 1 — Executive briefing

**Input:**

```text
Prepare me for my meeting with ACME.
```

**Expected path:** MCP + RAG + Agent synthesis

```mermaid
flowchart TB
    Q[Prepare ACME meeting] --> MCP[MCP: customer, sales, tickets, contracts]
    Q --> RAG[RAG: product docs, policies]
    MCP --> Brief[Executive Briefing]
    RAG --> Brief
    Brief --> UI[UI: FACT blocks + Sources + Recommendations]

    classDef path fill:#C8E6C9,stroke:#2E7D32,color:#1B5E20
    class MCP,RAG,Brief path
```

**Expected output (structure):**

- Customer summary
- Revenue / renewal
- Open issues
- Opportunities (AI RECOMMENDATION)
- Risks (FACT + RECOMMENDATION)
- Sources list

## Scenario 2 — Structured data only

**Input:** `How much did ACME spend last year?`

**Expected:** MCP → `get_customer_sales` — **no RAG**

**Interview talking point:** *"Revenue is transactional — it lives in the sales system, not in PDFs."*

## Scenario 3 — Knowledge only

**Input:** `What is our enterprise AI deployment policy?`

**Expected:** RAG → `ai-deployment-policy.md` — **no MCP**

**Talking point:** *"Policies change — they stay external to the model in Search index."*

## Scenario 4 — Product recommendation

**Input:** `What products should we recommend to ACME?`

**Expected:** MCP (history, current products) + RAG (product docs, compatibility)

## Scenario 5 — Renewal risk

**Input:** `What are the biggest risks to ACME's renewal?`

**Expected:** MCP (sales trend, tickets, contract) + RAG (renewal policy) + labeled reasoning

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant M as MCP
    participant R as RAG

    U->>A: Renewal risks for ACME?
    par Evidence
        A->>M: sales (-12%), tickets (3), contract (74d)
        A->>R: renewal policy, contract terms
    end
    A->>A: Separate FACT vs RECOMMENDATION
    A-->>U: Risk summary with citations
```

## UI mock — chat with sources

```text
┌──────────────────────────────────────────────┐
│ Enterprise AI Sales Intelligence             │
├──────────────────────────────────────────────┤
│ User: Prepare me for ACME.                   │
│                                              │
│ AI: ACME Executive Briefing                  │
│                                              │
│ FACT                                         │
│ Revenue decreased 12% during last quarter.   │
│                                              │
│ AI RECOMMENDATION                            │
│ Discuss adoption before expansion proposal.  │
│                                              │
│ Sources                                      │
│ • ACME Contract                              │
│ • Sales History                              │
│ • Support Tickets                            │
│ • renewal-policy.md                          │
├──────────────────────────────────────────────┤
│ Ask something...                       [Send] │
└──────────────────────────────────────────────┘
```

## Interview talking points (resumo)

| Question | Short answer |
|----------|----------------|
| Why Agent? | Dynamic tool selection per question |
| Why MCP? | Standard AI boundary over existing REST APIs |
| Why RAG? | Fresh organizational knowledge outside model weights |
| Why AI Search? | Hybrid + filter + scale |
| Why Semantic Kernel? | Microsoft orchestration + Azure integration |
| Why Container Apps? | Managed containers without K8s complexity |

## Next step

→ [07 — Development Phases](07-development-phases.md)
