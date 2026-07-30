from __future__ import annotations

import logging
from pathlib import Path

from fastapi import HTTPException

from app.agent.sk_agent import SemanticKernelSalesAgent
from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import ChatResponse
from app.rag.retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)


class SalesAgentOrchestrator:
    """Thin facade — all chat intelligence is delegated to the Semantic Kernel LLM agent."""

    def __init__(
        self,
        mcp_client: McpClient | None = None,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        self.mcp = mcp_client or McpClient()
        self.retriever = retriever or KnowledgeRetriever()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        path = Path(settings.prompts_dir) / "sales-agent.system.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return "You are an enterprise sales intelligence agent."

    async def handle(self, conversation_id: str, message: str) -> ChatResponse:
        if not settings.azure_openai_configured:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Azure OpenAI is not configured. Set AZURE_AI_ENDPOINT, "
                    "AZURE_AI_API_KEY, and AZURE_CHAT_DEPLOYMENT in .env."
                ),
            )

        agent = SemanticKernelSalesAgent(self.mcp, self.retriever, self.system_prompt)
        try:
            return await agent.handle(conversation_id, message)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Semantic Kernel agent failed")
            raise HTTPException(
                status_code=502,
                detail=f"Agent execution failed: {exc}",
            ) from exc
