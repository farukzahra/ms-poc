from __future__ import annotations

import logging
import re
from typing import Any

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from app.agent.plugins.mcp_plugin import McpPlugin
from app.agent.plugins.rag_plugin import RagPlugin
from app.agent.response_builder import (
    facts_from_tool_results,
    recommendations_from_context,
)
from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import ChatResponse, SourceItem
from app.rag.retriever import KnowledgeRetriever
from app.telemetry.tracer import AgentTracer

logger = logging.getLogger(__name__)


class SemanticKernelSalesAgent:
    """Azure OpenAI agent orchestrated via Semantic Kernel with MCP + RAG plugins."""

    def __init__(
        self,
        mcp_client: McpClient | None = None,
        retriever: KnowledgeRetriever | None = None,
        system_prompt: str = "",
    ) -> None:
        self.mcp_plugin = McpPlugin(mcp_client)
        self.rag_plugin = RagPlugin(retriever)
        self.system_prompt = system_prompt
        self.kernel = self._build_kernel()
        self.agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="SalesIntelligenceAgent",
            instructions=system_prompt,
            plugins=[self.mcp_plugin, self.rag_plugin],
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )

    def _build_kernel(self) -> Kernel:
        kernel = Kernel()
        kernel.add_service(
            AzureChatCompletion(
                service_id="chat",
                deployment_name=settings.azure_chat_deployment,
                endpoint=settings.azure_ai_endpoint,
                api_key=settings.azure_ai_api_key,
                api_version=settings.azure_openai_api_version,
            )
        )
        return kernel

    async def handle(self, conversation_id: str, message: str) -> ChatResponse:
        self.mcp_plugin.reset()
        self.rag_plugin.reset()
        tool_results: dict[str, Any] = {}

        with AgentTracer(conversation_id=conversation_id) as tracer:
            tracer.start_span("agent_execution")
            response = await self.agent.get_response(messages=message)
            tracer.end_span("agent_execution")

            message_content = response.message
            answer = (
                str(message_content.content)
                if message_content and message_content.content
                else "No answer generated."
            )
            if "FACT" not in answer:
                answer = self._ensure_sections(answer)

            for tool_name in self.mcp_plugin.tools_used:
                # Tool outputs are captured via plugin side effects; rebuild from MCP if needed
                tool_results[tool_name] = tool_results.get(tool_name)

            # Re-fetch structured data for facts when briefing tools were used
            await self._collect_tool_results(message, tool_results)

            sources = list({s.source: s for s in self.rag_plugin.sources}.values())
            facts = facts_from_tool_results(tool_results)
            recommendations = recommendations_from_context(tool_results, sources)

            usage = (message_content.metadata if message_content else {}) or {}
            token_in = usage.get("prompt_tokens") or usage.get("usage", {}).get("prompt_tokens")
            token_out = usage.get("completion_tokens") or usage.get("usage", {}).get(
                "completion_tokens"
            )
            if token_in or token_out:
                tracer.log_tokens(prompt=int(token_in or 0), completion=int(token_out or 0))

            tools_used = list(dict.fromkeys(self.mcp_plugin.tools_used))
            if self.rag_plugin.sources and "search_knowledge" not in tools_used:
                tools_used.append("search_knowledge")

            return ChatResponse(
                conversationId=conversation_id,
                answer=answer,
                sources=sources,
                toolsUsed=tools_used,
                facts=facts,
                recommendations=recommendations,
            )

    async def _collect_tool_results(self, message: str, tool_results: dict[str, Any]) -> None:
        from demo_data.store import DEMO_STORE

        customer = DEMO_STORE.customer_by_name_fragment(message.lower())
        if not customer:
            return
        customer_id = customer.id

        for tool_name in self.mcp_plugin.tools_used:
            if tool_name in tool_results and tool_results[tool_name]:
                continue
            raw = await self.mcp_plugin.mcp.call_tool(tool_name, {"customer_id": customer_id})
            tool_results[tool_name] = raw

    def _ensure_sections(self, answer: str) -> str:
        if re.search(r"^##?\s*FACT", answer, re.MULTILINE):
            return answer
        return f"## FACT\n{answer}"
