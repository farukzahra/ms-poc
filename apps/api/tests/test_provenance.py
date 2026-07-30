from app.agent.plugins.mcp_plugin import McpPlugin, PluginCallRecord
from app.agent.plugins.rag_plugin import RagPlugin
from app.agent.provenance import build_response_debug


def test_build_response_debug_mcp_rag_llm_pipeline():
    mcp = McpPlugin()
    mcp.call_records = [
        PluginCallRecord(
            tool="get_customer",
            arguments={"customer_id": "ACME-001"},
            result_preview='{"name":"ACME Corporation"}',
            duration_ms=12.3,
        ),
        PluginCallRecord(
            tool="get_customer_tickets",
            arguments={"customer_id": "ACME-001"},
            result_preview='{"open":3}',
            duration_ms=8.1,
        ),
    ]

    rag = RagPlugin()
    rag.call_records = [
        PluginCallRecord(
            tool="search_knowledge",
            arguments={"query": "renewal policy", "customer_id": "ACME-001"},
            result_preview='{"results":[{"title":"Renewal policy"}]}',
            duration_ms=45.0,
        ),
    ]

    debug = build_response_debug(
        mcp_plugin=mcp,
        rag_plugin=rag,
        prompt_tokens=1200,
        completion_tokens=450,
    )

    assert debug.pipeline == [
        "mcp:get_customer",
        "mcp:get_customer_tickets",
        "rag:search_knowledge",
        "llm:synthesis",
    ]
    assert len(debug.mcp_calls) == 2
    assert debug.mcp_calls[0].source == "mcp"
    assert debug.mcp_calls[0].tool == "get_customer"
    assert debug.rag_calls[0].source == "rag"
    assert debug.llm is not None
    assert debug.llm.prompt_tokens == 1200
    assert debug.llm.completion_tokens == 450
