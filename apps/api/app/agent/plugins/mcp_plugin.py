from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from semantic_kernel.functions import kernel_function

from app.mcp.client import McpClient


def _preview_result(result: object, limit: int = 280) -> str:
    text = json.dumps(result, default=str)
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"


@dataclass
class PluginCallRecord:
    tool: str
    arguments: dict[str, str] = field(default_factory=dict)
    result_preview: str = ""
    duration_ms: float | None = None


class McpPlugin:
    """Semantic Kernel plugin wrapping MCP enterprise tools."""

    def __init__(self, mcp_client: McpClient | None = None) -> None:
        self.mcp = mcp_client or McpClient()
        self.tools_used: list[str] = []
        self.call_records: list[PluginCallRecord] = []

    def reset(self) -> None:
        self.tools_used = []
        self.call_records = []

    async def _call(self, tool: str, arguments: dict[str, str]) -> str:
        started = time.perf_counter()
        result = await self.mcp.call_tool(tool, arguments)
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        self.tools_used.append(tool)
        self.call_records.append(
            PluginCallRecord(
                tool=tool,
                arguments=arguments,
                result_preview=_preview_result(result),
                duration_ms=duration_ms,
            )
        )
        return json.dumps(result)

    @kernel_function(
        name="get_customer",
        description="Fetch CRM profile for a customer ID (e.g. ACME-001)",
    )
    async def get_customer(self, customer_id: str) -> str:
        return await self._call("get_customer", {"customer_id": customer_id})

    @kernel_function(
        name="get_customer_sales",
        description="Fetch sales and revenue history for a customer",
    )
    async def get_customer_sales(self, customer_id: str) -> str:
        return await self._call("get_customer_sales", {"customer_id": customer_id})

    @kernel_function(
        name="get_customer_tickets",
        description="Fetch open and recent support tickets for a customer",
    )
    async def get_customer_tickets(self, customer_id: str) -> str:
        return await self._call("get_customer_tickets", {"customer_id": customer_id})

    @kernel_function(
        name="get_customer_contracts",
        description="Fetch contracts and renewal dates for a customer",
    )
    async def get_customer_contracts(self, customer_id: str) -> str:
        return await self._call("get_customer_contracts", {"customer_id": customer_id})

    @kernel_function(
        name="search_products",
        description="Search the enterprise product catalog",
    )
    async def search_products(self, query: str) -> str:
        return await self._call("search_products", {"query": query})
