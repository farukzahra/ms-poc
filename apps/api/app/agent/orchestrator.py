from __future__ import annotations

import logging
import re
from pathlib import Path

from demo_data.store import DEMO_STORE

from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import ChatResponse, FactItem, RecommendationItem, SourceItem
from app.rag.retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)

POLICY_KEYWORDS = (
    "policy",
    "policies",
    "renewal",
    "contract terms",
    "documentation",
    "according to",
    "governance",
    "deployment",
)
BRIEFING_KEYWORDS = ("prepare", "briefing", "meeting", "executive", "summary", "overview")
SALES_KEYWORDS = ("revenue", "sales", "spend", "trend", "annual")
TICKET_KEYWORDS = ("ticket", "support", "issue", "open")
CONTRACT_KEYWORDS = ("contract", "renewal date", "renewal")
PRODUCT_KEYWORDS = ("product", "catalog", "recommend", "upsell", "cross-sell")


def _resolve_customer_id(message: str) -> str | None:
    lowered = message.lower()
    match = DEMO_STORE.customer_by_name_fragment(lowered)
    return match.id if match else None


def _needs_rag(message: str) -> bool:
    lowered = message.lower()
    return any(keyword in lowered for keyword in POLICY_KEYWORDS)


def _needs_briefing(message: str) -> bool:
    lowered = message.lower()
    return any(keyword in lowered for keyword in BRIEFING_KEYWORDS)


class SalesAgentOrchestrator:
    def __init__(
        self,
        mcp_client: McpClient | None = None,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self.mcp = mcp_client or McpClient()
        self.retriever = retriever or KnowledgeRetriever()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        path = Path(settings.prompts_dir) / "sales-agent.system.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return "You are an enterprise sales intelligence agent."

    async def handle(self, conversation_id: str, message: str) -> ChatResponse:
        if settings.azure_openai_configured:
            try:
                from app.agent.azure_agent import AzureSalesAgent

                agent = AzureSalesAgent(self.mcp, self.retriever, self.system_prompt)
                return await agent.handle(conversation_id, message)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Azure agent failed, using local orchestrator: %s", exc)

        return await self._handle_local(conversation_id, message)

    async def _handle_local(self, conversation_id: str, message: str) -> ChatResponse:
        customer_id = _resolve_customer_id(message)
        tools_used: list[str] = []
        facts: list[FactItem] = []
        recommendations: list[RecommendationItem] = []
        sources: list[SourceItem] = []

        customer = None
        sales = None
        tickets = None
        contracts = None

        lowered = message.lower()

        if customer_id and (
            _needs_briefing(message)
            or any(keyword in lowered for keyword in ("customer", "account", "who is"))
            or not any(keyword in lowered for keyword in SALES_KEYWORDS + TICKET_KEYWORDS)
        ):
            customer = await self.mcp.call_tool("get_customer", {"customer_id": customer_id})
            tools_used.append("get_customer")

        if customer_id and (
            _needs_briefing(message) or any(keyword in lowered for keyword in SALES_KEYWORDS)
        ):
            sales = await self.mcp.call_tool("get_customer_sales", {"customer_id": customer_id})
            tools_used.append("get_customer_sales")

        if customer_id and (
            _needs_briefing(message) or any(keyword in lowered for keyword in TICKET_KEYWORDS)
        ):
            tickets = await self.mcp.call_tool(
                "get_customer_tickets", {"customer_id": customer_id}
            )
            tools_used.append("get_customer_tickets")

        if customer_id and (
            _needs_briefing(message) or any(keyword in lowered for keyword in CONTRACT_KEYWORDS)
        ):
            contracts = await self.mcp.call_tool(
                "get_customer_contracts", {"customer_id": customer_id}
            )
            tools_used.append("get_customer_contracts")

        if any(keyword in lowered for keyword in PRODUCT_KEYWORDS):
            query = "analytics" if "analytics" in lowered else "enterprise"
            await self.mcp.call_tool("search_products", {"query": query})
            tools_used.append("search_products")

        rag_hits: list[dict[str, str]] = []
        if _needs_rag(message) or _needs_briefing(message):
            rag_hits = await self.retriever.search(message, customer_id=customer_id)
            sources = [SourceItem(**item) for item in rag_hits]

        if customer:
            facts.append(FactItem(label="Customer", value=f"{customer['name']} ({customer['id']})"))
            facts.append(
                FactItem(
                    label="Annual revenue",
                    value=f"${customer['annualRevenue']:,.0f}",
                )
            )
            facts.append(
                FactItem(
                    label="Revenue trend",
                    value=f"{customer['revenueTrendPct']:+.1f}%",
                )
            )

        if sales:
            facts.append(
                FactItem(
                    label="2025 annual spend",
                    value=f"${sales['annualSpend2025']:,.0f}",
                )
            )
            facts.append(
                FactItem(
                    label="2024 annual spend",
                    value=f"${sales['annualSpend2024']:,.0f}",
                )
            )

        if tickets:
            facts.append(
                FactItem(label="Open tickets", value=str(tickets.get("openCount", 0)))
            )

        if contracts and contracts.get("contracts"):
            primary = contracts["contracts"][0]
            facts.append(
                FactItem(
                    label="Renewal",
                    value=f"{primary['renewalDate']} ({primary['renewalDaysRemaining']} days)",
                )
            )

        answer = self._compose_answer(
            customer=customer,
            sales=sales,
            tickets=tickets,
            contracts=contracts,
            sources=sources,
            facts=facts,
            recommendations=recommendations,
            message=message,
        )

        if customer and tickets and tickets.get("openCount", 0) >= 2:
            recommendations.append(
                RecommendationItem(
                    title="Resolve support escalations before renewal",
                    detail="Multiple open tickets increase renewal risk; align support and account team.",
                )
            )

        if customer and customer.get("revenueTrendPct", 0) < -5:
            recommendations.append(
                RecommendationItem(
                    title="Investigate adoption decline",
                    detail="Review product usage and schedule an executive check-in focused on value realization.",
                )
            )

        if rag_hits and any("renewal" in hit.get("source", "") for hit in rag_hits):
            recommendations.append(
                RecommendationItem(
                    title="Start renewal planning early",
                    detail="Policy recommends opening renewal discussions at least 90 days before expiration.",
                )
            )

        return ChatResponse(
            conversationId=conversation_id,
            answer=answer,
            sources=sources,
            toolsUsed=list(dict.fromkeys(tools_used)),
            facts=facts,
            recommendations=recommendations,
        )

    def _compose_answer(
        self,
        *,
        customer: dict | None,
        sales: dict | None,
        tickets: dict | None,
        contracts: dict | None,
        sources: list[SourceItem],
        facts: list[FactItem],
        recommendations: list[RecommendationItem],
        message: str,
    ) -> str:
        if not customer and not sources:
            return (
                "I could not identify a demo customer in your message. "
                "Try asking about ACME, Globex, or Initech."
            )

        lines: list[str] = []
        if customer:
            lines.append(f"# {customer['name']} Executive Briefing")
            lines.append("")
            lines.append("## FACT")
            lines.append(f"- Segment: {customer['segment']}")
            lines.append(f"- Annual revenue: ${customer['annualRevenue']:,.0f}")
            lines.append(f"- Revenue trend: {customer['revenueTrendPct']:+.1f}%")
            lines.append(f"- Account owner: {customer['accountOwner']}")

        if sales:
            lines.append(f"- 2025 spend: ${sales['annualSpend2025']:,.0f}")
            lines.append(f"- 2024 spend: ${sales['annualSpend2024']:,.0f}")

        if tickets:
            lines.append(f"- Open support tickets: {tickets.get('openCount', 0)}")
            for ticket in tickets.get("tickets", [])[:3]:
                if ticket.get("status") == "open":
                    lines.append(
                        f"  - {ticket['title']} ({ticket['priority']} priority, "
                        f"{ticket['openedDaysAgo']} days open)"
                    )

        if contracts and contracts.get("contracts"):
            primary = contracts["contracts"][0]
            lines.append(
                f"- Primary contract renewal: {primary['renewalDate']} "
                f"({primary['renewalDaysRemaining']} days remaining)"
            )

        if sources:
            lines.append("")
            lines.append("## Knowledge sources")
            for source in sources:
                lines.append(f"- {source.title} ({source.source})")

        if recommendations:
            lines.append("")
            lines.append("## RECOMMENDATION")
            for item in recommendations:
                lines.append(f"- **{item.title}**: {item.detail}")

        if not customer and sources:
            lines = ["# Policy answer", "", "## FACT"]
            for source in sources:
                snippet = source.snippet or ""
                lines.append(f"- {source.title}: {snippet[:180]}")

        return "\n".join(lines)
