from __future__ import annotations

import logging

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings

from app.agent.plugins.mcp_plugin import McpPlugin
from app.agent.plugins.rag_plugin import RagPlugin
from app.agent.provenance import build_response_debug
from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import ChatResponse
from app.rag.retriever import KnowledgeRetriever
from app.telemetry.tracer import AgentTracer

logger = logging.getLogger(__name__)


def extract_token_counts(metadata: object | None) -> tuple[int, int]:
    """Read prompt/completion tokens from SK metadata dict or CompletionUsage objects."""
    if metadata is None:
        return 0, 0

    usage: object = metadata
    if isinstance(metadata, dict):
        usage = metadata.get("usage", metadata)

    if isinstance(usage, dict):
        prompt = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
        completion = usage.get("completion_tokens") or usage.get("output_tokens") or 0
        return int(prompt), int(completion)

    prompt = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None) or 0
    completion = (
        getattr(usage, "completion_tokens", None)
        or getattr(usage, "output_tokens", None)
        or 0
    )
    return int(prompt), int(completion)


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

        with AgentTracer(conversation_id=conversation_id) as tracer:
            tracer.start_span("agent_execution")
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_completion_tokens=4096,
            )
            response = await self.agent.get_response(
                messages=message,
                settings=execution_settings,
            )
            tracer.end_span("agent_execution")

            message_content = response.message
            answer = (
                str(message_content.content)
                if message_content and message_content.content
                else "No answer generated."
            )

            sources = list({s.source: s for s in self.rag_plugin.sources}.values())
            tools_used = list(dict.fromkeys(self.mcp_plugin.tools_used))
            if self.rag_plugin.sources and "search_knowledge" not in tools_used:
                tools_used.append("search_knowledge")

            token_in, token_out = extract_token_counts(
                message_content.metadata if message_content else None
            )
            if token_in or token_out:
                tracer.log_tokens(prompt=token_in, completion=token_out)

            debug = build_response_debug(
                mcp_plugin=self.mcp_plugin,
                rag_plugin=self.rag_plugin,
                prompt_tokens=token_in,
                completion_tokens=token_out,
            )

            return ChatResponse(
                conversationId=conversation_id,
                answer=answer,
                sources=sources,
                toolsUsed=tools_used,
                facts=[],
                recommendations=[],
                debug=debug,
            )
