from __future__ import annotations

import json

from semantic_kernel.functions import kernel_function

from app.mcp.client import McpClient


class McpPlugin:
    """Semantic Kernel plugin wrapping MCP enterprise tools."""

    def __init__(self, mcp_client: McpClient | None = None) -> None:
        self.mcp = mcp_client or McpClient()
        self.tools_used: list[str] = []

    def reset(self) -> None:
        self.tools_used = []

    @kernel_function(
        name="get_customer",
        description="Fetch CRM profile for a customer ID (e.g. ACME-001)",
    )
    async def get_customer(self, customer_id: str) -> str:
        result = await self.mcp.call_tool("get_customer", {"customer_id": customer_id})
        self.tools_used.append("get_customer")
        return json.dumps(result)

    @kernel_function(
        name="get_customer_sales",
        description="Fetch sales and revenue history for a customer",
    )
    async def get_customer_sales(self, customer_id: str) -> str:
        result = await self.mcp.call_tool("get_customer_sales", {"customer_id": customer_id})
        self.tools_used.append("get_customer_sales")
        return json.dumps(result)

    @kernel_function(
        name="get_customer_tickets",
        description="Fetch open and recent support tickets for a customer",
    )
    async def get_customer_tickets(self, customer_id: str) -> str:
        result = await self.mcp.call_tool("get_customer_tickets", {"customer_id": customer_id})
        self.tools_used.append("get_customer_tickets")
        return json.dumps(result)

    @kernel_function(
        name="get_customer_contracts",
        description="Fetch contracts and renewal dates for a customer",
    )
    async def get_customer_contracts(self, customer_id: str) -> str:
        result = await self.mcp.call_tool(
            "get_customer_contracts", {"customer_id": customer_id}
        )
        self.tools_used.append("get_customer_contracts")
        return json.dumps(result)

    @kernel_function(
        name="search_products",
        description="Search the enterprise product catalog",
    )
    async def search_products(self, query: str) -> str:
        result = await self.mcp.call_tool("search_products", {"query": query})
        self.tools_used.append("search_products")
        return json.dumps(result)
