from __future__ import annotations

import json

from app.agent.plugins.mcp_plugin import McpPlugin
from app.agent.plugins.rag_plugin import RagPlugin
from app.config import settings
from app.models.chat import DebugStep, LlmDebugInfo, ResponseDebug, ToolCallDebug


def _format_args(arguments: dict[str, str]) -> str:
    if not arguments:
        return "(no arguments)"
    parts = [f"{key}={value}" for key, value in arguments.items()]
    return ", ".join(parts)


def _summarize_tool_result(preview: str, max_len: int = 120) -> str:
    if not preview:
        return "(empty response)"
    try:
        parsed = json.loads(preview)
        if isinstance(parsed, dict):
            if "name" in parsed:
                segment = parsed.get("segment", "")
                suffix = f" ({segment})" if segment else ""
                return f"{parsed['name']}{suffix}"
            if "open" in parsed:
                return f"{parsed['open']} open ticket(s)"
            if "results" in parsed and isinstance(parsed["results"], list):
                count = len(parsed["results"])
                titles = [
                    item.get("title", "")
                    for item in parsed["results"][:2]
                    if isinstance(item, dict)
                ]
                titles = [title for title in titles if title]
                if titles:
                    joined = ", ".join(titles)
                    extra = f" (+{count - len(titles)} more)" if count > len(titles) else ""
                    return f"{count} document(s): {joined}{extra}"
                return f"{count} document(s) retrieved"
        text = json.dumps(parsed, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        text = preview
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 1]}…"


def _mcp_step(call: ToolCallDebug, index: int) -> DebugStep:
    return DebugStep(
        id=f"mcp-{index}-{call.tool}",
        kind="mcp",
        title=f"Called MCP tool: {call.tool}",
        input_summary=_format_args(call.arguments),
        output_summary=_summarize_tool_result(call.result_preview),
        duration_ms=call.duration_ms,
        raw={
            "arguments": call.arguments,
            "resultPreview": call.result_preview,
        },
    )


def _rag_step(call: ToolCallDebug, index: int) -> DebugStep:
    return DebugStep(
        id=f"rag-{index}-{call.tool}",
        kind="rag",
        title=f"Retrieved documents: {call.tool}",
        input_summary=_format_args(call.arguments),
        output_summary=_summarize_tool_result(call.result_preview),
        duration_ms=call.duration_ms,
        raw={
            "arguments": call.arguments,
            "resultPreview": call.result_preview,
        },
    )


def _llm_step(llm: LlmDebugInfo) -> DebugStep:
    return DebugStep(
        id="llm-synthesis",
        kind="llm",
        title="Sent tool results to LLM for synthesis",
        input_summary=(
            f"Model {llm.model} · {llm.prompt_tokens} prompt token(s) "
            f"(MCP/RAG context + user message)"
        ),
        output_summary=(
            f"{llm.completion_tokens} completion token(s) · executive briefing answer"
        ),
        raw={
            "model": llm.model,
            "promptTokens": llm.prompt_tokens,
            "completionTokens": llm.completion_tokens,
            "note": llm.note,
        },
    )


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

    llm: LlmDebugInfo | None = None
    if prompt_tokens or completion_tokens:
        llm = LlmDebugInfo(
            model=settings.azure_chat_deployment or "azure-openai",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    pipeline: list[str] = []
    steps: list[DebugStep] = []

    for index, call in enumerate(mcp_calls):
        pipeline.append(f"mcp:{call.tool}")
        steps.append(_mcp_step(call, index))

    for index, call in enumerate(rag_calls):
        pipeline.append(f"rag:{call.tool}")
        steps.append(_rag_step(call, index))

    if llm is not None:
        pipeline.append("llm:synthesis")
        steps.append(_llm_step(llm))

    return ResponseDebug(
        steps=steps,
        pipeline=pipeline,
        mcp_calls=mcp_calls,
        rag_calls=rag_calls,
        llm=llm,
    )
