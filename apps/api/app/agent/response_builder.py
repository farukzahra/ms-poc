from __future__ import annotations

import json
from typing import Any

from app.models.chat import FactItem, RecommendationItem, SourceItem


def facts_from_tool_results(tool_results: dict[str, Any]) -> list[FactItem]:
    facts: list[FactItem] = []
    customer = tool_results.get("get_customer")
    if isinstance(customer, dict):
        facts.append(
            FactItem(label="Customer", value=f"{customer['name']} ({customer['id']})")
        )
        facts.append(
            FactItem(label="Annual revenue", value=f"${customer['annualRevenue']:,.0f}")
        )
        facts.append(
            FactItem(label="Revenue trend", value=f"{customer['revenueTrendPct']:+.1f}%")
        )

    sales = tool_results.get("get_customer_sales")
    if isinstance(sales, dict):
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

    tickets = tool_results.get("get_customer_tickets")
    if isinstance(tickets, dict):
        facts.append(FactItem(label="Open tickets", value=str(tickets.get("openCount", 0))))

    contracts = tool_results.get("get_customer_contracts")
    if isinstance(contracts, dict) and contracts.get("contracts"):
        primary = contracts["contracts"][0]
        facts.append(
            FactItem(
                label="Renewal",
                value=f"{primary['renewalDate']} ({primary['renewalDaysRemaining']} days)",
            )
        )
    return facts


def recommendations_from_context(
    tool_results: dict[str, Any],
    sources: list[SourceItem],
) -> list[RecommendationItem]:
    items: list[RecommendationItem] = []
    customer = tool_results.get("get_customer")
    tickets = tool_results.get("get_customer_tickets")

    if isinstance(customer, dict) and isinstance(tickets, dict):
        if tickets.get("openCount", 0) >= 2:
            items.append(
                RecommendationItem(
                    title="Resolve support escalations before renewal",
                    detail="Multiple open tickets increase renewal risk; align support and account team.",
                )
            )
        if customer.get("revenueTrendPct", 0) < -5:
            items.append(
                RecommendationItem(
                    title="Investigate adoption decline",
                    detail="Review product usage and schedule an executive check-in focused on value realization.",
                )
            )

    if any("renewal" in (s.source or "").lower() for s in sources):
        items.append(
            RecommendationItem(
                title="Start renewal planning early",
                detail="Policy recommends opening renewal discussions at least 90 days before expiration.",
            )
        )
    return items


def parse_tool_result(name: str, raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw
