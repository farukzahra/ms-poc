import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_acme_briefing_local(monkeypatch):
    async def fake_call_tool(name: str, arguments: dict):
        mapping = {
            "get_customer": {
                "id": "ACME-001",
                "name": "ACME Corporation",
                "segment": "Enterprise",
                "annualRevenue": 2_400_000,
                "revenueTrendPct": -12.0,
                "renewalDays": 74,
                "products": ["Analytics Platform"],
                "accountOwner": "jane.smith@company.com",
            },
            "get_customer_sales": {
                "customerId": "ACME-001",
                "annualSpend2025": 2_400_000,
                "annualSpend2024": 2_720_000,
                "transactions": [],
            },
            "get_customer_tickets": {
                "customerId": "ACME-001",
                "openCount": 3,
                "tickets": [],
            },
            "get_customer_contracts": {
                "customerId": "ACME-001",
                "contracts": [
                    {
                        "id": "C-9001",
                        "title": "ACME Enterprise Agreement 2026",
                        "renewalDate": "2026-09-12",
                        "renewalDaysRemaining": 74,
                        "annualValue": 2_400_000,
                        "sourceFile": "contract-acme-2026.pdf",
                    }
                ],
            },
        }
        return mapping[name]

    class FakeMcp:
        async def call_tool(self, name: str, arguments: dict):
            return await fake_call_tool(name, arguments)

        async def health_check(self) -> bool:
            return True

    monkeypatch.setattr("app.agent.orchestrator.McpClient", FakeMcp)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "conversationId": "test-1",
                "message": "Prepare me for my meeting with ACME",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "ACME" in body["answer"]
    assert "get_customer" in body["toolsUsed"]
    assert "get_customer_sales" in body["toolsUsed"]
