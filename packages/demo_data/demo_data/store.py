from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    segment: str
    annual_revenue: float
    revenue_trend_pct: float
    renewal_days: int
    products: list[str]
    account_owner: str


@dataclass(frozen=True)
class SaleRecord:
    id: str
    customer_id: str
    year: int
    amount: float
    product: str
    quarter: str


@dataclass(frozen=True)
class Ticket:
    id: str
    customer_id: str
    title: str
    status: str
    priority: str
    opened_days_ago: int


@dataclass(frozen=True)
class Contract:
    id: str
    customer_id: str
    title: str
    renewal_date: str
    renewal_days_remaining: int
    annual_value: float
    source_file: str


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    description: str
    target_segment: str


@dataclass
class DemoStore:
    customers: dict[str, Customer]
    sales: list[SaleRecord]
    tickets: list[Ticket]
    contracts: list[Contract]
    products: dict[str, Product]

    def customer_by_name_fragment(self, text: str) -> Customer | None:
        lowered = text.lower()
        for customer in self.customers.values():
            if customer.name.lower().split()[0] in lowered or customer.id.lower() in lowered:
                return customer
        if "acme" in lowered:
            return self.customers.get("ACME-001")
        if "globex" in lowered:
            return self.customers.get("GLOBEX-001")
        if "initech" in lowered:
            return self.customers.get("INITECH-001")
        return None


def _build_store() -> DemoStore:
    customers = {
        "ACME-001": Customer(
            id="ACME-001",
            name="ACME Corporation",
            segment="Enterprise",
            annual_revenue=2_400_000,
            revenue_trend_pct=-12.0,
            renewal_days=74,
            products=["Analytics Platform", "Enterprise Platform"],
            account_owner="jane.smith@company.com",
        ),
        "GLOBEX-001": Customer(
            id="GLOBEX-001",
            name="Globex Corporation",
            segment="Mid-Market",
            annual_revenue=980_000,
            revenue_trend_pct=8.0,
            renewal_days=120,
            products=["Analytics Platform"],
            account_owner="alex.jones@company.com",
        ),
        "INITECH-001": Customer(
            id="INITECH-001",
            name="Initech",
            segment="Enterprise",
            annual_revenue=1_550_000,
            revenue_trend_pct=-3.0,
            renewal_days=45,
            products=["Enterprise Platform"],
            account_owner="samir.nagheb@company.com",
        ),
    }
    sales = [
        SaleRecord("S-1001", "ACME-001", 2025, 2_400_000, "Enterprise Platform", "Q4"),
        SaleRecord("S-1002", "ACME-001", 2024, 2_720_000, "Enterprise Platform", "Q4"),
        SaleRecord("S-1003", "ACME-001", 2025, 450_000, "Analytics Platform", "Q2"),
        SaleRecord("S-2001", "GLOBEX-001", 2025, 980_000, "Analytics Platform", "Q3"),
        SaleRecord("S-3001", "INITECH-001", 2025, 1_550_000, "Enterprise Platform", "Q1"),
    ]
    tickets = [
        Ticket("T-501", "ACME-001", "Dashboard export timeout", "open", "high", 12),
        Ticket("T-502", "ACME-001", "SSO metadata sync delay", "open", "medium", 8),
        Ticket("T-503", "ACME-001", "API rate limit clarification", "open", "low", 3),
        Ticket("T-601", "GLOBEX-001", "User provisioning question", "closed", "low", 20),
        Ticket("T-701", "INITECH-001", "Contract amendment request", "open", "medium", 5),
    ]
    contracts = [
        Contract(
            "C-9001",
            "ACME-001",
            "ACME Enterprise Agreement 2026",
            "2026-09-12",
            74,
            2_400_000,
            "contract-acme-2026.pdf",
        ),
        Contract(
            "C-9002",
            "GLOBEX-001",
            "Globex Analytics Subscription",
            "2026-11-28",
            120,
            980_000,
            "contract-globex-2026.pdf",
        ),
        Contract(
            "C-9003",
            "INITECH-001",
            "Initech Platform Renewal",
            "2026-06-14",
            45,
            1_550_000,
            "contract-initech-2026.pdf",
        ),
    ]
    products = {
        "PRD-ANALYTICS": Product(
            "PRD-ANALYTICS",
            "Analytics Platform",
            "Analytics",
            "Self-service analytics with enterprise governance.",
            "Enterprise",
        ),
        "PRD-ENTERPRISE": Product(
            "PRD-ENTERPRISE",
            "Enterprise Platform",
            "Platform",
            "Core enterprise workflow and integration platform.",
            "Enterprise",
        ),
        "PRD-AI-AUTO": Product(
            "PRD-AI-AUTO",
            "AI Automation Suite",
            "AI",
            "Copilot workflows for sales and support teams.",
            "Enterprise",
        ),
    }
    return DemoStore(
        customers=customers,
        sales=sales,
        tickets=tickets,
        contracts=contracts,
        products=products,
    )


DEMO_STORE = _build_store()


def customer_to_dict(customer: Customer) -> dict[str, Any]:
    return {
        "id": customer.id,
        "name": customer.name,
        "segment": customer.segment,
        "annualRevenue": customer.annual_revenue,
        "revenueTrendPct": customer.revenue_trend_pct,
        "renewalDays": customer.renewal_days,
        "products": customer.products,
        "accountOwner": customer.account_owner,
    }
