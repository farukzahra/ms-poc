from __future__ import annotations

import json
import logging
from typing import Any

from mcp.client import Client
from mcp_types import TextContent

from app.config import settings

logger = logging.getLogger(__name__)


class McpClient:
    """Call MCP tools using the MCP 2.0 streamable HTTP client."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.mcp_server_url).rstrip("/")

    @property
    def _mcp_url(self) -> str:
        return f"{self.base_url}/mcp"

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with Client(self._mcp_url) as client:
            result = await client.call_tool(name, arguments)
            structured = getattr(result, "structured_content", None)
            if structured is not None:
                if isinstance(structured, dict):
                    return structured
                return {"data": structured}
            if result.content:
                block = result.content[0]
                if isinstance(block, TextContent):
                    try:
                        return json.loads(block.text)
                    except json.JSONDecodeError:
                        return {"text": block.text}
            return {"raw": result.model_dump()}

    async def health_check(self) -> bool:
        try:
            async with Client(self._mcp_url) as client:
                tools = await client.list_tools()
                return bool(tools.tools)
        except Exception as exc:  # noqa: BLE001
            logger.debug("MCP health check failed: %s", exc)
            return False
