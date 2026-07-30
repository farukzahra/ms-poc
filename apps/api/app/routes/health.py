from fastapi import APIRouter

from app.config import settings
from app.mcp.client import McpClient
from app.models.chat import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    mcp_ok = await McpClient().health_check()
    return ReadyResponse(
        status="ok" if mcp_ok else "degraded",
        mcp="ok" if mcp_ok else "unavailable",
        rag="azure" if settings.azure_search_configured else "local",
        llm="azure" if settings.azure_openai_configured else "local",
    )
