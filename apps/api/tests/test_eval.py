import json
from pathlib import Path

import pytest

EVAL_PATH = Path(__file__).resolve().parents[3] / "data" / "eval" / "tool-selection.json"

pytestmark = pytest.mark.skip(
    reason="Tool selection is LLM-driven; run data/eval with llm-evaluation against Azure OpenAI."
)


@pytest.fixture
def eval_cases() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    json.loads(EVAL_PATH.read_text(encoding="utf-8")),
    ids=lambda c: c["id"],
)
async def test_eval_tool_selection(case, monkeypatch):
    pytest.skip("Replaced by LLM evaluation — see data/eval/tool-selection.json")
