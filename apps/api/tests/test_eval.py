import json
from pathlib import Path

import pytest

from app.agent.orchestrator import SalesAgentOrchestrator

EVAL_PATH = Path(__file__).resolve().parents[3] / "data" / "eval" / "tool-selection.json"


@pytest.fixture
def eval_cases() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
@pytest.mark.parametrize("case", json.loads(EVAL_PATH.read_text(encoding="utf-8")), ids=lambda c: c["id"])
async def test_eval_tool_selection(case, monkeypatch):
    async def fake_call_tool(name: str, arguments: dict):
        return {"tool": name, "arguments": arguments}

    class FakeMcp:
        async def call_tool(self, name: str, arguments: dict):
            return await fake_call_tool(name, arguments)

        async def health_check(self) -> bool:
            return True

    monkeypatch.setattr("app.agent.orchestrator.McpClient", FakeMcp)

    orchestrator = SalesAgentOrchestrator()
    response = await orchestrator.handle("eval", case["message"])

    if case.get("expectedTool"):
        assert case["expectedTool"] in response.tools_used
    if case.get("expectedTools"):
        for tool in case["expectedTools"]:
            assert tool in response.tools_used
    if case.get("expectRag"):
        assert response.sources or "search_knowledge" in response.tools_used
