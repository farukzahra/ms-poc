import pytest

from app.agent.response_builder import facts_from_tool_results, recommendations_from_context
from app.models.chat import SourceItem


def test_facts_from_customer_and_sales():
    facts = facts_from_tool_results(
        {
            "get_customer": {
                "id": "ACME-001",
                "name": "ACME Corporation",
                "annualRevenue": 2_400_000,
                "revenueTrendPct": -12.0,
            },
            "get_customer_sales": {
                "annualSpend2025": 2_400_000,
                "annualSpend2024": 2_720_000,
            },
        }
    )
    labels = {fact.label for fact in facts}
    assert "Customer" in labels
    assert "2025 annual spend" in labels


def test_recommendations_for_open_tickets():
    items = recommendations_from_context(
        {
            "get_customer": {"revenueTrendPct": 0},
            "get_customer_tickets": {"openCount": 3},
        },
        [],
    )
    assert any("support" in item.title.lower() for item in items)


def test_recommendations_from_renewal_source():
    items = recommendations_from_context(
        {},
        [SourceItem(title="Renewal", source="policies/renewal-policy.md")],
    )
    assert items
