# Azure access — agent bootstrap checklist

What the agent needs to connect **ms-poc** to Azure **without asking you for manual steps** on every run.

## Current status (agent-checked)

| Prerequisite | Status | Notes |
|--------------|--------|-------|
| Azure CLI | Installed (`pip install azure-cli`, v2.88) | `python -m azure.cli` |
| `az login` | **Done** | `farukz@gmail.com` / Azure subscription 1 |
| Subscription ID | `85167153-f689-43e4-9ff5-72f98346f07b` | saved in `vps-secrets/azure-subscription-id.txt` |
| Resource group | **`rg-ai-sales-poc`** (eastus) | provisioned |
| Azure OpenAI | **`oai-ms-poc`** | deployments: `gpt-5-mini`, `text-embedding-3-small` |
| Azure AI Search | **`search-ms-poc`** (Basic) | index `enterprise-knowledge` (4 docs ingested) |
| Blob Storage | **`stmspoc85167153`** | container `documents/` |
| `.env` | **Filled** | via `scripts/azure_fill_env.py` (gitignored) |
| `/ready` | **`llm: azure`, `rag: azure`** | validated |

## What the agent can do with privileges

Once **`az login`** succeeds and the account has the roles below, the agent can run:

```powershell
# From repo root (after az login)
.\scripts\azure-discover.ps1    # list OpenAI, Search, Storage in subscription
.\scripts\azure-fill-env.ps1    # write non-secret refs + keys into .env (gitignored)
docker compose up -d --force-recreate api
```

The agent should **never commit** `.env` or paste keys into chat/docs.

## Minimum Azure RBAC (subscription or resource group `rg-ai-sales-poc`)

| Role | Why |
|------|-----|
| **Contributor** (or scoped equivalent) | Create/update OpenAI, Search, Storage, Container Apps |
| **Cognitive Services OpenAI User** | List keys + deployments on Azure OpenAI / Foundry |
| **Search Service Contributor** | Create index, run ingest |
| **Storage Blob Data Contributor** | Upload `data/` to documents container |

For POC cost control, prefer a **dedicated resource group** with budget alert (~$50/month per `docs/cost.md`).

## Services to provision (Phase 2–4)

| Service | Purpose | Env vars filled |
|---------|---------|-----------------|
| Azure OpenAI / Foundry | Chat + embeddings | `AZURE_AI_*`, deployments |
| Azure AI Search | RAG index | `AZURE_SEARCH_*` |
| Azure Blob Storage | Document source | `AZURE_STORAGE_*` |

Optional (Phase 5–6): Container Apps, Key Vault, Application Insights, Entra app registration.

## One-time actions only you can unblock

These **cannot** be fully automated by the agent:

1. **`az login`** (or service principal) — first authentication on this machine
2. **Subscription choice** — if multiple subscriptions
3. **Billing / quota** — enabling OpenAI on subscription, accepting Foundry terms
4. **Entra admin consent** — if org policy blocks resource creation

Everything else (discover resources, pull keys, fill `.env`, ingest, restart stack, validate `/ready`) the agent should do alone.

## Recommended: store agent-usable secrets (optional)

Add to `C:\repo\financeiro\planos\vps-secrets\` (never commit):

```
azure-service-principal.json   # appId, tenantId, clientSecret (if not using az login)
azure-subscription-id.txt      # optional default subscription
```

Then the agent can run `az login --service-principal ...` without asking again.

## Verify connection

After fill:

```bash
curl http://localhost:8000/ready
# Expect: "llm":"azure" and/or "rag":"azure" when configured and tested
```

Do **not** claim Azure works until chat + ingest succeed against real services (`AGENTS.md`).
