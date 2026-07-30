from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    message: str

    model_config = {"populate_by_name": True}


class SourceItem(BaseModel):
    title: str
    source: str
    snippet: str | None = None


class FactItem(BaseModel):
    label: str
    value: str


class RecommendationItem(BaseModel):
    title: str
    detail: str


class ChatResponse(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    answer: str
    sources: list[SourceItem] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list, alias="toolsUsed")
    facts: list[FactItem] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class HealthResponse(BaseModel):
    status: str
    service: str = "enterprise-api"


class ReadyResponse(BaseModel):
    status: str
    mcp: str
    rag: str
    llm: str
