import pytest
from httpx import ASGITransport, AsyncClient

from app.agent.orchestrator import SalesAgentOrchestrator
from app.agent.plugins.mcp_plugin import PluginCallRecord
from app.agent.provenance import build_response_debug
from app.config import Settings
from app.main import app
from app.models.chat import ChatResponse


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_requires_azure_openai(monkeypatch):
    monkeypatch.setattr(
        Settings,
        "azure_openai_configured",
        property(lambda self: False),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "conversationId": "test-1",
                "message": "Prepare me for my meeting with ACME",
            },
        )

    assert response.status_code == 503
    assert "Azure OpenAI" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_acme_briefing(monkeypatch):
    async def fake_handle(
        self: SalesAgentOrchestrator,
        conversation_id: str,
        message: str,
    ) -> ChatResponse:
        return ChatResponse(
            conversationId=conversation_id,
            answer=(
                "# ACME Corporation Executive Briefing\n\n"
                "## FACT\n"
                "- Revenue trend: -12.0%\n\n"
                "## RECOMMENDATION\n"
                "- Resolve open support tickets before renewal."
            ),
            sources=[],
            toolsUsed=[
                "get_customer",
                "get_customer_sales",
                "get_customer_tickets",
            ],
            facts=[],
            recommendations=[],
            debug=build_response_debug(
                mcp_plugin=type(
                    "M",
                    (),
                    {
                        "call_records": [
                            PluginCallRecord(
                                tool="get_customer",
                                arguments={"customer_id": "ACME-001"},
                                result_preview='{"segment":"Enterprise"}',
                                duration_ms=10.0,
                            ),
                        ],
                    },
                )(),
                rag_plugin=type("R", (), {"call_records": []})(),
                prompt_tokens=500,
                completion_tokens=200,
            ),
        )

    monkeypatch.setattr(SalesAgentOrchestrator, "handle", fake_handle)

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
    assert body["debug"]["mcpCalls"][0]["tool"] == "get_customer"
    assert "llm:synthesis" in body["debug"]["pipeline"]
    assert len(body["debug"]["steps"]) >= 2
    assert body["debug"]["steps"][0]["kind"] == "mcp"
