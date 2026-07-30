from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import AsyncAzureOpenAI

from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import ChatResponse, SourceItem
from app.rag.retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "Fetch CRM profile for a customer ID",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_sales",
            "description": "Fetch sales and revenue data",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_tickets",
            "description": "Fetch support tickets",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_contracts",
            "description": "Fetch contracts and renewal dates",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search product catalog",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search policy and contract documents (RAG)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "customer_id": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
]


class AzureSalesAgent:
    def __init__(
        self,
        mcp_client: McpClient,
        retriever: KnowledgeRetriever,
        system_prompt: str,
    ) -> None:
        self.mcp = mcp_client
        self.retriever = retriever
        self.system_prompt = system_prompt
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_ai_endpoint,
            api_key=settings.azure_ai_api_key,
            api_version="2024-10-21",
        )

    async def handle(self, conversation_id: str, message: str) -> ChatResponse:
        tools_used: list[str] = []
        sources: list[SourceItem] = []
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message},
        ]

        for _ in range(6):
            response = await self.client.chat.completions.create(
                model=settings.azure_chat_deployment,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            choice = response.choices[0]
            assistant_message = choice.message
            if assistant_message.tool_calls:
                messages.append(assistant_message.model_dump())
                for tool_call in assistant_message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or "{}")
                    if name == "search_knowledge":
                        hits = await self.retriever.search(
                            args.get("query", message),
                            customer_id=args.get("customer_id"),
                        )
                        tool_result = {"results": hits}
                        sources.extend(SourceItem(**item) for item in hits)
                        tools_used.append("search_knowledge")
                    else:
                        tool_result = await self.mcp.call_tool(name, args)
                        tools_used.append(name)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        }
                    )
                continue

            answer = assistant_message.content or "No answer generated."
            if "FACT" not in answer:
                answer = self._ensure_sections(answer)
            return ChatResponse(
                conversationId=conversation_id,
                answer=answer,
                sources=list({s.source: s for s in sources}.values()),
                toolsUsed=list(dict.fromkeys(tools_used)),
            )

        return ChatResponse(
            conversationId=conversation_id,
            answer="Unable to complete agent loop.",
            sources=sources,
            toolsUsed=list(dict.fromkeys(tools_used)),
        )

    def _ensure_sections(self, answer: str) -> str:
        if re.search(r"^##?\s*FACT", answer, re.MULTILINE):
            return answer
        return f"## FACT\n{answer}"
