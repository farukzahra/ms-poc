# Enterprise AI Sales Intelligence Agent — Plano POC

> Especificação completa para a POC Microsoft Azure AI Solution Engineering.
> Origem: `PLAN.MD.txt`. Última atualização: 2026-07-30.

## Índice

1. [Objetivo](#1-objective)
2. [Cenário de negócio](#2-business-scenario)
3. [Valor de negócio](#3-business-value)
4. [Arquitetura Azure alvo](#4-target-azure-architecture)
5. [Por que estas tecnologias](#5-why-these-technologies)
6. [Stack tecnológico](#6-technology-stack)
7. [Estrutura do repositório](#7-repository-structure)
8. [Resource Group Azure](#8-azure-resource-group)
9. [Proteção de budget](#9-azure-budget-protection)
10. [Azure OpenAI / Foundry](#10-azure-openai--microsoft-foundry)
11. [Azure AI Search](#11-azure-ai-search)
12. [Ingestão de documentos](#12-document-ingestion)
13. [Chunking](#13-chunking)
14. [RAG](#14-rag)
15. [Citações](#15-citations)
16. [APIs enterprise](#16-enterprise-apis)
17. [MCP Server](#17-mcp-server)
18. [Agent](#18-agent)
19. [System prompt](#19-agent-system-prompt)
20. [Conversa exemplo](#20-example-conversation)
21. [Fato vs recomendação](#21-fact-vs-recommendation)
22. [Segurança](#22-security)
23. [Secrets](#23-secrets)
24. [Observabilidade](#24-observability)
25. [AI Observability](#25-ai-observability)
26. [Responsible AI](#26-responsible-ai)
27. [Frontend](#27-frontend)
28. [API](#28-api)
29. [Health](#29-health)
30. [Docker](#30-docker)
31. [Azure Container Apps](#31-azure-container-apps)
32. [Infrastructure as Code](#32-infrastructure-as-code)
33. [Azure CLI](#33-azure-cli)
34. [Configuração](#34-configuration)
35. [Estratégia de custo](#35-cost-strategy)
36. [Estratégia de desenvolvimento (fases)](#36-development-strategy)
37. [Dataset demo](#37-demo-dataset)
38. [Clientes demo](#38-demo-customers)
39. [Cenários demo](#39-demo-scenarios)
40. [ADRs](#40-architecture-decision-records)
41. [Testes](#41-testing)
42. [Avaliação](#42-evaluation)
43. [Performance](#43-performance)
44. [Arquitetura produção](#44-production-architecture)
45. [Evolução de segurança](#45-security-evolution)
46. [Evolução da arquitetura AI](#46-ai-architecture-evolution)
47. [Métricas de negócio](#47-business-metrics)
48. [Demo final](#48-final-demo)
49. [Talking points entrevista](#49-interview-talking-points)
50. [Princípio arquitetural](#50-important-architectural-principle)
51. [Definition of Done](#51-definition-of-done)
52. [Primeira task de implementação](#52-first-implementation-task)

---
# Enterprise AI Sales Intelligence Agent

## Microsoft Azure AI Solution Engineering POC

## 1. Objective

Build an enterprise-grade Proof of Concept demonstrating how Microsoft Azure AI technologies can be used to create an AI-powered Sales Intelligence platform.

The system will combine:

* Microsoft Foundry / Azure OpenAI
* Azure AI Search
* RAG
* AI Agents
* MCP
* Semantic Kernel
* Python
* FastAPI
* Vue 3
* Azure Blob Storage
* Azure Container Apps
* Microsoft Entra ID
* Application Insights
* Docker

The POC should demonstrate the architecture, engineering practices, security, observability, and business value expected from an **AI & Apps Solution Engineer**.

The system must be designed around a realistic enterprise scenario rather than being a generic chatbot.

---

## 2. Business Scenario

Large enterprise sales organizations usually have customer information distributed across multiple systems.

For a single customer, a salesperson may need to consult:

* CRM
* sales history
* contracts
* support tickets
* product documentation
* pricing information
* customer documentation
* internal policies
* previous interactions

The objective is to build an AI Sales Intelligence Agent capable of combining structured and unstructured information.

The user should be able to ask:

```text
Prepare me for my meeting with ACME.
```

The agent should retrieve:

* customer information
* sales history
* open support issues
* contracts
* relevant product information
* relevant internal documentation

and produce an executive briefing.

---

## 3. Business Value

The solution should demonstrate measurable business value.

Potential benefits:

* reduce time spent preparing for customer meetings
* increase seller productivity
* identify expansion opportunities
* identify renewal risks
* improve customer knowledge
* reduce time searching enterprise documentation
* provide consistent access to company knowledge
* accelerate decision making

The POC should therefore not be presented as:

> "An AI chatbot."

It should be presented as:

> "An enterprise AI agent that combines organizational knowledge with operational business systems to improve sales productivity and customer intelligence."

---

## 4. Target Azure Architecture

The target architecture is:

```text
                         SALES USER
                              â”‚
                              â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚    Vue 3 UI     â”‚
                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
                              â–¼
                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                  â”‚   Azure Container     â”‚
                  â”‚       Apps            â”‚
                  â”‚                       â”‚
                  â”‚  Python + FastAPI     â”‚
                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
                              â–¼
                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                  â”‚   Semantic Kernel     â”‚
                  â”‚      AI Agent         â”‚
                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
                 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                 â”‚                         â”‚
                 â–¼                         â–¼
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚       RAG       â”‚       â”‚   MCP Client    â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                 â”‚                         â”‚
                 â–¼                         â–¼
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚ Azure AI Search â”‚       â”‚   MCP Server    â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                 â”‚                         â”‚
                 â”‚                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                 â”‚                â–¼        â–¼         â–¼
                 â”‚              CRM      Sales    Tickets
                 â”‚              API       API       API
                 â”‚
                 â–¼
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚ Azure Blob      â”‚
        â”‚ Storage         â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

                              â”‚
                              â–¼
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ Microsoft Foundry â”‚
                    â”‚ / Azure OpenAI    â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

                              â”‚
                              â–¼
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ Application       â”‚
                    â”‚ Insights          â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 5. Why These Technologies

## Microsoft Foundry / Azure OpenAI

Used for:

* LLM inference
* embeddings
* agent reasoning
* tool calling

The implementation should use the current Microsoft-supported SDK/API approach.

Do not hardcode deprecated Azure OpenAI API versions.

---

## Azure AI Search

Used as the enterprise knowledge retrieval layer.

The POC should demonstrate:

* vector search
* keyword search
* hybrid search
* semantic ranking where available
* metadata filtering

The architecture should clearly separate:

```text
LLM
```

from:

```text
Retrieval
```

The LLM must not be treated as the company's knowledge database.

---

## Azure Blob Storage

Used as the source document repository.

Example:

```text
documents/
    customers/
    products/
    contracts/
    policies/
    sales/
```

Documents should be indexed into Azure AI Search.

---

## Semantic Kernel

Use Semantic Kernel as the primary agent/orchestration framework.

The agent should be responsible for:

* understanding user intent
* deciding which tools are necessary
* calling MCP tools
* requesting RAG information
* synthesizing information
* generating grounded responses

Keep orchestration logic separate from HTTP controllers.

---

## MCP

MCP should expose enterprise capabilities to the AI agent.

Example tools:

```text
get_customer
get_customer_sales
get_customer_tickets
get_customer_contracts
search_products
get_product
```

The MCP server should internally call enterprise REST APIs.

The architecture should demonstrate:

```text
Existing REST APIs
       â†“
    MCP Server
       â†“
    AI Agent
```

The existing enterprise APIs must not be rewritten specifically for AI.

---

## 6. Technology Stack

## Backend

```text
Python 3.12+
FastAPI
Pydantic
Semantic Kernel
MCP Python SDK
httpx
pytest
```

## Frontend

```text
Vue 3
Vite
TypeScript
```

## Azure

```text
Microsoft Foundry / Azure OpenAI
Azure AI Search
Azure Blob Storage
Azure Container Apps
Microsoft Entra ID
Application Insights
Azure Monitor
Azure Key Vault
```

## Development

```text
Docker
Docker Compose
Azure CLI
Git
```

---

## 7. Repository Structure

Create a monorepo:

```text
enterprise-ai-sales/
â”‚
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”‚   â”œâ”€â”€ agent/
â”‚   â”‚   â”‚   â”œâ”€â”€ rag/
â”‚   â”‚   â”‚   â”œâ”€â”€ mcp/
â”‚   â”‚   â”‚   â”œâ”€â”€ domain/
â”‚   â”‚   â”‚   â”œâ”€â”€ infrastructure/
â”‚   â”‚   â”‚   â””â”€â”€ main.py
â”‚   â”‚   â””â”€â”€ tests/
â”‚   â”‚
â”‚   â”œâ”€â”€ mcp-server/
â”‚   â”‚   â”œâ”€â”€ server/
â”‚   â”‚   â””â”€â”€ tests/
â”‚   â”‚
â”‚   â””â”€â”€ web/
â”‚       â”œâ”€â”€ src/
â”‚       â””â”€â”€ tests/
â”‚
â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ mock-crm/
â”‚   â”œâ”€â”€ mock-sales/
â”‚   â””â”€â”€ mock-tickets/
â”‚
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ customers/
â”‚   â”œâ”€â”€ products/
â”‚   â”œâ”€â”€ contracts/
â”‚   â””â”€â”€ policies/
â”‚
â”œâ”€â”€ infrastructure/
â”‚   â””â”€â”€ azure/
â”‚       â”œâ”€â”€ bicep/
â”‚       â””â”€â”€ scripts/
â”‚
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ architecture.md
â”‚   â”œâ”€â”€ security.md
â”‚   â”œâ”€â”€ rag.md
â”‚   â”œâ”€â”€ mcp.md
â”‚   â”œâ”€â”€ observability.md
â”‚   â””â”€â”€ cost.md
â”‚
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ Makefile
â”œâ”€â”€ .env.example
â””â”€â”€ README.md
```

---

## 8. Azure Resource Group

Use one dedicated resource group.

Example:

```bash
az group create \
  --name rg-ai-sales-poc \
  --location eastus
```

Use one region consistently.

Do not randomly create resources in multiple regions.

---

## 9. Azure Budget Protection

Cost control is mandatory.

The project must document how to configure:

* Azure budget
* cost alerts
* resource cleanup
* resource shutdown

Example conceptual budget:

```text
Budget: $50
Alert: 50%
Alert: 75%
Alert: 90%
Alert: 100%
```

The POC should not assume that having $200 in Azure credits means $200 should be spent.

The objective is to demonstrate the architecture while keeping consumption low.

---

## 10. Azure OpenAI / Microsoft Foundry

Create the required AI resource using the current Azure/Microsoft Foundry workflow.

Deploy:

```text
A small/low-cost chat model
```

and:

```text
A small embedding model
```

Do not deploy unnecessarily expensive models.

The exact model names must be configurable.

Example:

```env
AZURE_AI_ENDPOINT=
AZURE_AI_API_KEY=
AZURE_CHAT_DEPLOYMENT=
AZURE_EMBEDDING_DEPLOYMENT=
```

Do not commit credentials.

---

## 11. Azure AI Search

Create one Azure AI Search service.

The POC should create an index such as:

```text
enterprise-knowledge
```

Suggested fields:

```text
id
content
title
document_type
customer_id
department
source
created_at
content_vector
```

The vector field must use the embedding dimensions of the selected embedding model.

Do not hardcode embedding dimensions without verifying the selected model.

---

## 12. Document Ingestion

Implement an ingestion command:

```bash
python -m app.rag.ingest
```

The pipeline:

```text
Blob Storage
      â”‚
      â–¼
Document Loader
      â”‚
      â–¼
Text Extraction
      â”‚
      â–¼
Chunking
      â”‚
      â–¼
Metadata Extraction
      â”‚
      â–¼
Embedding Generation
      â”‚
      â–¼
Azure AI Search
```

Support at least:

```text
Markdown
TXT
PDF
JSON
```

For the initial POC, documents may be simple deterministic sample files.

---

## 13. Chunking

Implement configurable chunking.

Example configuration:

```env
CHUNK_SIZE=800
CHUNK_OVERLAP=120
```

The implementation must allow these values to be changed without modifying source code.

The README should explain why chunk size and overlap affect retrieval quality.

---

## 14. RAG

The RAG service should expose a clean interface:

```python
class KnowledgeRetriever:
    async def search(
        self,
        query: str,
        customer_id: str | None = None
    ):
        ...
```

The implementation should perform:

```text
Query
 â†“
Embedding
 â†“
Hybrid Search
 â†“
Metadata filtering
 â†“
Ranking
 â†“
Top K documents
```

Example:

```text
customer_id = ACME-001
```

should be used as a filter whenever the question concerns ACME.

---

## 15. Citations

Every RAG answer should include citations.

Example:

```text
According to the customer contract, ACME's renewal
period begins 90 days before expiration.

Sources:
- contract-acme-2026.pdf
- renewal-policy.md
```

The UI should make the sources visible.

The agent must never claim that information came from a source that was not actually retrieved.

---

## 16. Enterprise APIs

Create mock REST services representing existing enterprise systems.

## CRM

```http
GET /customers/{customerId}
```

## Sales

```http
GET /customers/{customerId}/sales
```

## Tickets

```http
GET /customers/{customerId}/tickets
```

## Contracts

```http
GET /customers/{customerId}/contracts
```

## Products

```http
GET /products
GET /products/{productId}
```

These services should contain deterministic sample data.

---

## 17. MCP Server

The MCP server should expose the enterprise APIs as tools.

Example:

```text
get_customer
get_customer_sales
get_customer_tickets
get_customer_contracts
search_products
get_product
```

The MCP server must not contain duplicated enterprise business logic.

It should act as an AI integration boundary.

Architecture:

```text
AI Agent
   â”‚
   â–¼
MCP Client
   â”‚
   â–¼
MCP Server
   â”‚
   â–¼
REST APIs
```

---

## 18. Agent

Implement a Sales Intelligence Agent using Semantic Kernel.

The agent must be able to determine:

```text
Does this question require:

1. RAG?
2. MCP?
3. Both?
4. Neither?
```

Examples:

### Question

```text
How much did ACME spend last year?
```

Expected:

```text
MCP â†’ Sales API
```

Do not use RAG.

---

### Question

```text
What is our enterprise AI deployment policy?
```

Expected:

```text
RAG â†’ Azure AI Search
```

Do not call CRM APIs.

---

### Question

```text
What are the biggest risks for ACME's renewal?
```

Expected:

```text
MCP
+
RAG
```

The agent should combine:

* sales
* tickets
* contract information
* internal policies

---

## 19. Agent System Prompt

Create a system prompt that establishes:

```text
You are an Enterprise Sales Intelligence Agent.

Your job is to help authorized sales users understand
customers and identify opportunities.

You have access to:

1. Enterprise operational systems through MCP.
2. Enterprise knowledge through RAG.

Rules:

- Never invent customer data.
- Prefer structured systems for transactional information.
- Use RAG for organizational knowledge and documents.
- Use both when necessary.
- Clearly distinguish facts from recommendations.
- Cite retrieved documents.
- Respect authorization boundaries.
- If evidence is insufficient, explicitly say so.
- Never expose internal system credentials.
```

The prompt should be stored outside application code.

---

## 20. Example Conversation

User:

```text
Prepare me for my meeting with ACME.
```

Agent:

```text
ACME Executive Briefing

Customer:
ACME Corporation

Current Revenue:
$2.4M annually

Renewal:
74 days remaining

Current Products:
Analytics Platform
Enterprise Platform

Open Support Issues:
3

Revenue Trend:
-12% over the previous quarter

Key Opportunities:
1. Analytics expansion
2. AI automation
3. Enterprise licensing

Key Risks:
1. Revenue decline
2. Open support tickets
3. Renewal discussion has not started

Recommended Talking Points:
1. Address support issues.
2. Discuss Analytics expansion.
3. Introduce AI automation capabilities.

Sources:
- CRM
- Sales system
- Support system
- Contract
- Product documentation
```

---

## 21. Fact vs Recommendation

The application must visually distinguish:

```text
FACT
```

from:

```text
AI RECOMMENDATION
```

Example:

```text
FACT

ACME's revenue decreased 12% during the last quarter.


AI RECOMMENDATION

Discuss whether the decrease is related to reduced
product adoption before presenting an expansion proposal.
```

Recommendations must be clearly identified as AI-generated.

---

## 22. Security

Implement authentication using Microsoft Entra ID if practical for the deployed version.

The API must support an authenticated identity.

Define roles:

```text
SALES_REP
SALES_MANAGER
ADMIN
```

Customer access must be authorized.

The system should never rely solely on:

```text
customer_id
```

provided by the frontend for authorization.

The backend must derive authorization from the authenticated identity.

---

## 23. Secrets

Never store:

```text
API keys
passwords
tokens
client secrets
```

in Git.

Local development:

```text
.env
```

Azure:

```text
Azure Key Vault
```

Environment variables should contain only references/configuration where possible.

---

## 24. Observability

Integrate Application Insights.

Capture:

```text
request_id
user_id
conversation_id
customer_id
agent_execution_time
LLM_latency
LLM_token_usage
RAG_latency
MCP_latency
tool_name
retrieved_documents
errors
```

Do not log sensitive customer information unnecessarily.

The system should provide enough telemetry to answer:

> "Why did this agent response take 5 seconds?"

---

## 25. AI Observability

Track each agent execution:

```text
Agent execution
    â”‚
    â”œâ”€â”€ LLM call
    â”œâ”€â”€ MCP call
    â”œâ”€â”€ RAG search
    â”œâ”€â”€ LLM call
    â””â”€â”€ Final response
```

Example telemetry:

```text
Agent Execution
----------------------------

Duration: 3.2 seconds

LLM calls: 2

MCP:
  get_customer: 120ms
  get_sales: 180ms
  get_tickets: 150ms

RAG:
  search: 220ms

Documents:
  5 retrieved

Tokens:
  input: 2,300
  output: 650
```

---

## 26. Responsible AI

The system should implement basic responsible AI controls.

The agent must:

* avoid hallucinations
* provide citations
* distinguish facts from recommendations
* respect authorization
* avoid unnecessary PII exposure
* explicitly state uncertainty
* refuse unsupported conclusions

Example:

```text
I found evidence of a 12% revenue decline.

However, the available data does not establish
the cause of the decline.
```

---

## 27. Frontend

Build a simple Vue 3 interface.

Required features:

* chat interface
* conversation history
* sources
* tool usage
* loading indicator
* errors
* customer context

Example:

```text
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Enterprise AI Sales Intelligence             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                              â”‚
â”‚ User                                         â”‚
â”‚ Prepare me for ACME.                         â”‚
â”‚                                              â”‚
â”‚ AI                                             â”‚
â”‚                                              â”‚
â”‚ ACME Executive Briefing                      â”‚
â”‚                                              â”‚
â”‚ FACT                                         â”‚
â”‚ Revenue decreased 12%.                       â”‚
â”‚                                              â”‚
â”‚ AI RECOMMENDATION                            â”‚
â”‚ Discuss adoption before expansion.           â”‚
â”‚                                              â”‚
â”‚ Sources                                      â”‚
â”‚ â€¢ ACME Contract                              â”‚
â”‚ â€¢ Sales History                              â”‚
â”‚ â€¢ Support Tickets                            â”‚
â”‚                                              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Ask something...                       [Send] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Do not spend significant time on visual design.

Architecture and functionality are more important.

---

## 28. API

Expose:

```http
POST /api/v1/chat
```

Request:

```json
{
  "conversationId": "abc-123",
  "message": "Prepare me for my meeting with ACME"
}
```

Response:

```json
{
  "conversationId": "abc-123",
  "answer": "...",
  "sources": [
    {
      "title": "ACME Contract",
      "source": "contract-acme.pdf"
    }
  ],
  "toolsUsed": [
    "get_customer",
    "get_customer_sales",
    "get_customer_tickets"
  ]
}
```

---

## 29. Health

Implement:

```http
GET /health
GET /ready
```

Readiness should verify critical dependencies.

Do not expose secrets or connection strings.

---

## 30. Docker

The complete local development environment should run with:

```bash
docker compose up
```

Local services:

```text
Vue
FastAPI
MCP Server
Mock CRM
Mock Sales
Mock Tickets
```

Azure services remain external.

---

## 31. Azure Container Apps

Deploy the API to Azure Container Apps.

The container should:

* listen on the configured port
* expose `/health`
* use environment variables
* emit structured logs
* avoid local persistent storage

The frontend may be deployed separately.

---

## 32. Infrastructure as Code

Use Bicep.

Create:

```text
infrastructure/azure/bicep/
```

with modules for:

```text
resource-group
container-apps
storage
ai-search
monitoring
key-vault
```

The infrastructure should be reproducible.

Do not create production resources manually if they can be represented in Bicep.

---

## 33. Azure CLI

Document commands for:

```bash
az login
az account show
az group create
az deployment group create
az containerapp create
```

Do not hardcode subscription IDs.

Use:

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
```

where appropriate.

---

## 34. Configuration

Create:

```text
.env.example
```

Example:

```env
AZURE_AI_ENDPOINT=
AZURE_CHAT_DEPLOYMENT=
AZURE_EMBEDDING_DEPLOYMENT=

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_INDEX=

AZURE_STORAGE_ACCOUNT=

APPLICATIONINSIGHTS_CONNECTION_STRING=

MCP_SERVER_URL=
CRM_API_URL=
SALES_API_URL=
TICKETS_API_URL=
```

Never commit `.env`.

---

## 35. Cost Strategy

The POC is being developed using Azure credits.

The implementation should minimize unnecessary costs.

Principles:

1. Use small/appropriate AI models.
2. Avoid unnecessary LLM calls.
3. Cache embeddings.
4. Do not regenerate embeddings for unchanged documents.
5. Keep the dataset small.
6. Avoid always-on expensive compute.
7. Delete unused resources.
8. Configure Azure budgets and alerts.
9. Use local Docker for mock enterprise systems.
10. Shut down or delete resources when not actively demonstrating the POC.

The project should include:

```text
docs/cost.md
```

explaining which resources consume money and how to minimize them.

---

## 36. Development Strategy

Do NOT create all Azure resources immediately.

Implement in stages.

## Phase 1

Local:

```text
FastAPI
Semantic Kernel
MCP
Mock APIs
Vue
```

Use a simple local model or mocked LLM interface if necessary.

---

## Phase 2

Add:

```text
Azure OpenAI / Microsoft Foundry
```

Validate:

```text
LLM
tool calling
agent
```

---

## Phase 3

Add:

```text
Azure AI Search
```

Implement:

```text
document ingestion
embeddings
hybrid search
citations
```

---

## Phase 4

Add:

```text
Azure Blob Storage
```

Use Blob as the document source.

---

## Phase 5

Deploy:

```text
FastAPI â†’ Azure Container Apps
```

---

## Phase 6

Add:

```text
Application Insights
Entra ID
Key Vault
```

---

## 37. Demo Dataset

Create a fictional enterprise called:

```text
ACME Corporation
```

Create at least:

```text
3 customers
10 products
3 contracts
10 support tickets
10 sales transactions
5 company policies
5 product documents
```

The dataset should be fictional.

Do not use real customer data.

---

## 38. Demo Customers

Create:

```text
ACME Corporation
Globex Corporation
Initech
```

Each should have:

* profile
* revenue
* products
* contracts
* support tickets
* sales history

The data should contain intentional relationships so the Agent can reason over them.

Example:

```text
ACME

Revenue:
-12%

Support:
3 open tickets

Contract:
Renewal in 74 days

Product:
Analytics Platform

Opportunity:
Enterprise AI Automation
```

---

## 39. Demo Scenarios

## Scenario 1

```text
Prepare me for my meeting with ACME.
```

Expected:

```text
MCP + RAG
```

---

## Scenario 2

```text
How much did ACME spend last year?
```

Expected:

```text
MCP
```

---

## Scenario 3

```text
What is our enterprise AI deployment policy?
```

Expected:

```text
RAG
```

---

## Scenario 4

```text
What products should we recommend to ACME?
```

Expected:

```text
MCP + RAG
```

---

## Scenario 5

```text
What are the biggest risks to ACME's renewal?
```

Expected:

```text
MCP + RAG + Agent reasoning
```

---

## 40. Architecture Decision Records

Create ADRs for important decisions.

At minimum:

```text
ADR-001 â€” Why Semantic Kernel
ADR-002 â€” Why MCP
ADR-003 â€” Why Azure AI Search
ADR-004 â€” RAG vs structured API access
ADR-005 â€” Local development vs Azure
ADR-006 â€” Agent security model
```

Each ADR should explain:

```text
Context
Decision
Alternatives
Trade-offs
Consequences
```

This is important for the Solution Engineer interview.

---

## 41. Testing

Implement:

## Unit tests

* agent services
* RAG services
* MCP tools
* authorization
* API validation

## Integration tests

Test:

```text
Agent â†’ MCP â†’ REST API
```

and:

```text
Agent â†’ RAG â†’ Azure AI Search
```

## End-to-end test

Test:

```text
User
 â†“
API
 â†“
Agent
 â†“
MCP + RAG
 â†“
Response
```

---

## 42. Evaluation

Create a small evaluation dataset.

Example:

```json
{
  "question": "How much did ACME spend last year?",
  "expectedTool": "get_customer_sales"
}
```

Another:

```json
{
  "question": "What is our enterprise AI deployment policy?",
  "expectedSource": "RAG"
}
```

Evaluate:

* correctness
* grounding
* citation accuracy
* tool selection
* hallucination rate

The goal is to demonstrate that an AI application should be **evaluated**, not merely demonstrated.

---

## 43. Performance

Measure:

```text
first token latency
total response latency
LLM latency
RAG latency
MCP latency
```

Document possible optimization strategies:

* caching
* parallel tool calls
* smaller prompts
* fewer retrieved chunks
* reranking
* model selection
* asynchronous execution

---

## 44. Production Architecture

The final README must contain a section:

# From POC to Production

Explain how the system would evolve.

POC:

```text
Single Agent
Small dataset
Few users
Limited integrations
```

Production:

```text
Multi-agent architecture
Enterprise identity
Fine-grained authorization
Private networking
Private endpoints
Managed identities
Key Vault
Azure Monitor
Application Insights
CI/CD
Infrastructure as Code
Data governance
Model evaluation
Human approval workflows
Disaster recovery
High availability
Cost management
```

---

## 45. Security Evolution

Explain how production would use:

```text
Microsoft Entra ID
Managed Identity
Azure Key Vault
Private Endpoints
VNet integration
RBAC
Azure Policy
Defender for Cloud
```

Do not implement every component in the POC unless necessary.

The objective is to demonstrate that the architecture can evolve securely.

---

## 46. AI Architecture Evolution

Explain how the single agent could evolve into:

```text
                   Supervisor Agent
                          â”‚
             â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
             â–¼            â–¼            â–¼
        Sales Agent   Support Agent  Product Agent
             â”‚            â”‚            â”‚
             â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                          â–¼
                    Enterprise Data
```

This should be presented as a future architecture rather than unnecessarily implemented in the first POC.

---

## 47. Business Metrics

Define hypothetical metrics that could be measured in a real deployment:

```text
Meeting preparation time
Seller productivity
Customer research time
Opportunity identification
Renewal risk identification
AI response accuracy
Grounded response rate
Tool selection accuracy
User adoption
```

Example target:

```text
Reduce customer meeting preparation
from 30 minutes to less than 5 minutes.
```

This is a target for the POC demonstration, not a measured production result.

---

## 48. Final Demo

The final demo should take approximately 10 minutes.

## 1. Business problem

Explain fragmented enterprise information.

## 2. Architecture

Show:

```text
Azure OpenAI
Azure AI Search
MCP
Semantic Kernel
Container Apps
```

## 3. Customer briefing

Ask:

```text
Prepare me for my meeting with ACME.
```

## 4. Structured data

Ask:

```text
How much did ACME spend last year?
```

Show MCP.

## 5. Knowledge retrieval

Ask:

```text
What is our enterprise AI deployment policy?
```

Show RAG.

## 6. Combined reasoning

Ask:

```text
What are the biggest risks to ACME's renewal?
```

Show:

```text
MCP + RAG + Agent
```

## 7. Observability

Show Application Insights.

## 8. Architecture discussion

Explain:

* security
* scalability
* governance
* cost
* production evolution

---

## 49. Interview Talking Points

The developer should be able to explain:

### Why Agent?

Because the system must dynamically determine which enterprise capabilities are required.

### Why MCP?

Because MCP provides a standardized interface between AI agents and enterprise capabilities without requiring the underlying systems to be rewritten.

### Why RAG?

Because enterprise knowledge changes frequently and should remain external to the model.

### Why Azure AI Search?

Because enterprise retrieval requires hybrid/vector search, filtering, ranking, and scalable indexing.

### Why Semantic Kernel?

Because it provides an orchestration abstraction for AI applications and integrates naturally with the Microsoft AI ecosystem.

### Why Azure Container Apps?

Because the POC requires a simple managed container platform without introducing unnecessary Kubernetes complexity.

### Why separate MCP from REST APIs?

Because REST APIs serve traditional applications while MCP provides an AI-oriented tool interface.

---

## 50. Important Architectural Principle

The system must NOT become:

```text
User
 â†“
LLM
 â†“
Everything
```

Instead:

```text
                     USER
                       â”‚
                       â–¼
                    AGENT
                   /     \
                  /       \
                 â–¼         â–¼
              RAG          MCP
               â”‚            â”‚
               â–¼            â–¼
          Knowledge     Enterprise
             Base          APIs
```

The LLM should orchestrate access to enterprise capabilities rather than becoming the source of truth.

---

## 51. Definition of Done

The project is complete when:

* [ ] Vue application works.
* [ ] FastAPI backend works.
* [ ] Semantic Kernel agent works.
* [ ] MCP server works.
* [ ] Mock enterprise APIs work.
* [ ] Azure OpenAI / Microsoft Foundry works.
* [ ] Azure AI Search works.
* [ ] Blob Storage works.
* [ ] RAG works.
* [ ] Hybrid search works.
* [ ] Citations work.
* [ ] MCP tools work.
* [ ] Agent can choose MCP vs RAG.
* [ ] Authentication works for deployed version.
* [ ] Application Insights receives telemetry.
* [ ] Bicep infrastructure exists.
* [ ] Docker Compose works locally.
* [ ] Automated tests exist.
* [ ] Evaluation dataset exists.
* [ ] Cost documentation exists.
* [ ] Architecture documentation exists.
* [ ] Final demo can be completed in approximately 10 minutes.

---

## 52. First Implementation Task

Do not implement the entire system at once.

Start with:

```text
Phase 1

FastAPI
+
Semantic Kernel
+
MCP Server
+
Mock CRM
+
Mock Sales
+
Mock Tickets
+
Vue
```

Create one working vertical slice:

```text
User
 â†“
Vue
 â†“
FastAPI
 â†“
Semantic Kernel Agent
 â†“
MCP
 â†“
CRM API
 â†“
Answer
```

Only after this works should RAG and Azure AI Search be introduced.

Then integrate:

```text
Azure OpenAI
 â†“
Azure AI Search
 â†“
Blob Storage
 â†“
Container Apps
 â†“
Application Insights
```

At every stage, keep the application executable.

Do not generate placeholder implementations for completed components.

Do not claim Azure functionality works until it has been tested against the real Azure service.

