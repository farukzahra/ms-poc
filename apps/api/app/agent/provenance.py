from __future__ import annotations

from app.agent.plugins.mcp_plugin import McpPlugin
from app.agent.plugins.rag_plugin import RagPlugin
from app.config import settings
from app.models.chat import LlmDebugInfo, ResponseDebug, ToolCallDebug


def build_response_debug(
    *,
    mcp_plugin: McpPlugin,
    rag_plugin: RagPlugin,
    prompt_tokens: int,
    completion_tokens: int,
) -> ResponseDebug:
    """Assemble MCP / RAG / LLM provenance for the chat response."""
    mcp_calls = [
        ToolCallDebug(
            tool=record.tool,
            source="mcp",
            arguments=record.arguments,
            result_preview=record.result_preview,
            duration_ms=record.duration_ms,
        )
        for record in mcp_plugin.call_records
    ]
    rag_calls = [
        ToolCallDebug(
            tool=record.tool,
            source="rag",
            arguments=record.arguments,
            result_preview=record.result_preview,
            duration_ms=record.duration_ms,
        )
        for record in rag_plugin.call_records
    ]

    pipeline: list[str] = []
    for call in mcp_calls:
        pipeline.append(f"mcp:{call.tool}")
    for call in rag_calls:
        pipeline.append(f"rag:{call.tool}")
    if prompt_tokens or completion_tokens:
        pipeline.append("llm:synthesis")

    return ResponseDebug(
        pipeline=pipeline,
        mcp_calls=mcp_calls,
        rag_calls=rag_calls,
        llm=LlmDebugInfo(
            model=settings.azure_chat_deployment or "azure-openai",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        ),
    )
