from __future__ import annotations

from fastapi import FastAPI, HTTPException

from demo_data.store import DEMO_STORE, customer_to_dict


def create_crm_app() -> FastAPI:
    app = FastAPI(title="Mock CRM", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-crm"}

    @app.get("/customers/{customer_id}")
    async def get_customer(customer_id: str) -> dict:
        customer = DEMO_STORE.customers.get(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer_to_dict(customer)

    return app


def create_sales_app() -> FastAPI:
    app = FastAPI(title="Mock Sales", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-sales"}

    @app.get("/customers/{customer_id}/sales")
    async def get_sales(customer_id: str) -> dict:
        if customer_id not in DEMO_STORE.customers:
            raise HTTPException(status_code=404, detail="Customer not found")
        records = [s for s in DEMO_STORE.sales if s.customer_id == customer_id]
        total = sum(r.amount for r in records if r.year == 2025)
        prior = sum(r.amount for r in records if r.year == 2024)
        return {
            "customerId": customer_id,
            "annualSpend2025": total,
            "annualSpend2024": prior,
            "transactions": [
                {
                    "id": r.id,
                    "year": r.year,
                    "amount": r.amount,
                    "product": r.product,
                    "quarter": r.quarter,
                }
                for r in records
            ],
        }

    return app


def create_tickets_app() -> FastAPI:
    app = FastAPI(title="Mock Tickets", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-tickets"}

    @app.get("/customers/{customer_id}/tickets")
    async def get_tickets(customer_id: str) -> dict:
        if customer_id not in DEMO_STORE.customers:
            raise HTTPException(status_code=404, detail="Customer not found")
        records = [t for t in DEMO_STORE.tickets if t.customer_id == customer_id]
        open_tickets = [t for t in records if t.status == "open"]
        return {
            "customerId": customer_id,
            "openCount": len(open_tickets),
            "tickets": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "openedDaysAgo": t.opened_days_ago,
                }
                for t in records
            ],
        }

    return app


def create_contracts_app() -> FastAPI:
    app = FastAPI(title="Mock Contracts", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-contracts"}

    @app.get("/customers/{customer_id}/contracts")
    async def get_contracts(customer_id: str) -> dict:
        if customer_id not in DEMO_STORE.customers:
            raise HTTPException(status_code=404, detail="Customer not found")
        records = [c for c in DEMO_STORE.contracts if c.customer_id == customer_id]
        return {
            "customerId": customer_id,
            "contracts": [
                {
                    "id": c.id,
                    "title": c.title,
                    "renewalDate": c.renewal_date,
                    "renewalDaysRemaining": c.renewal_days_remaining,
                    "annualValue": c.annual_value,
                    "sourceFile": c.source_file,
                }
                for c in records
            ],
        }

    return app


def create_products_app() -> FastAPI:
    app = FastAPI(title="Mock Products", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-products"}

    @app.get("/products")
    async def list_products(q: str | None = None) -> dict:
        items = list(DEMO_STORE.products.values())
        if q:
            needle = q.lower()
            items = [
                p
                for p in items
                if needle in p.name.lower() or needle in p.description.lower()
            ]
        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "description": p.description,
                    "targetSegment": p.target_segment,
                }
                for p in items
            ]
        }

    @app.get("/products/{product_id}")
    async def get_product(product_id: str) -> dict:
        product = DEMO_STORE.products.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "description": product.description,
            "targetSegment": product.target_segment,
        }

    return app
