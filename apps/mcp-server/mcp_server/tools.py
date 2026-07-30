from __future__ import annotations

import httpx
from mcp.server.mcpserver import MCPServer

from mcp_server.config import settings

server = MCPServer("enterprise-sales-tools")


async def _get(client: httpx.AsyncClient, url: str, **params: str) -> dict:
    response = await client.get(url, params=params or None, timeout=10.0)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict):
        return payload
    return {"data": payload}


@server.tool()
async def get_customer(customer_id: str) -> dict:
    """Fetch CRM profile for a customer by ID (e.g. ACME-001)."""
    async with httpx.AsyncClient() as client:
        return await _get(client, f"{settings.crm_api_url}/customers/{customer_id}")


@server.tool()
async def get_customer_sales(customer_id: str) -> dict:
    """Fetch sales history and annual spend for a customer."""
    async with httpx.AsyncClient() as client:
        return await _get(client, f"{settings.sales_api_url}/customers/{customer_id}/sales")


@server.tool()
async def get_customer_tickets(customer_id: str) -> dict:
    """Fetch support tickets for a customer."""
    async with httpx.AsyncClient() as client:
        return await _get(client, f"{settings.tickets_api_url}/customers/{customer_id}/tickets")


@server.tool()
async def get_customer_contracts(customer_id: str) -> dict:
    """Fetch active contracts and renewal dates for a customer."""
    async with httpx.AsyncClient() as client:
        return await _get(
            client, f"{settings.contracts_api_url}/customers/{customer_id}/contracts"
        )


@server.tool()
async def search_products(query: str) -> dict:
    """Search the product catalog by keyword."""
    async with httpx.AsyncClient() as client:
        return await _get(client, f"{settings.products_api_url}/products", q=query)


@server.tool()
async def get_product(product_id: str) -> dict:
    """Fetch a single product by ID."""
    async with httpx.AsyncClient() as client:
        return await _get(client, f"{settings.products_api_url}/products/{product_id}")
