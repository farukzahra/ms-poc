from fastapi import APIRouter, Depends

from app.agent.orchestrator import SalesAgentOrchestrator
from app.auth.entra import get_current_user
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse, response_model_by_alias=True)
async def chat(
    request: ChatRequest,
    _user: dict | None = Depends(get_current_user),
) -> ChatResponse:
    orchestrator = SalesAgentOrchestrator()
    return await orchestrator.handle(request.conversation_id, request.message)
