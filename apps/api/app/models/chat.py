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


class ToolCallDebug(BaseModel):
    """One tool invocation with enough detail to trace data provenance."""

    tool: str
    source: str = Field(description="Origin layer: mcp or rag")
    arguments: dict[str, str] = Field(default_factory=dict)
    result_preview: str = Field(
        default="",
        alias="resultPreview",
        description="Truncated JSON returned by the tool (for debugging)",
    )
    duration_ms: float | None = Field(default=None, alias="durationMs")

    model_config = {"populate_by_name": True}


class LlmDebugInfo(BaseModel):
    """LLM synthesis metadata — narrative and recommendations come from here."""

    model: str
    role: str = "synthesis"
    prompt_tokens: int = Field(default=0, alias="promptTokens")
    completion_tokens: int = Field(default=0, alias="completionTokens")
    note: str = (
        "FACT bullets grounded in MCP/RAG tool results; "
        "RECOMMENDATION section is LLM-generated guidance."
    )

    model_config = {"populate_by_name": True}


class ResponseDebug(BaseModel):
    """Structured provenance for a chat response (MCP vs RAG vs LLM)."""

    pipeline: list[str] = Field(
        default_factory=list,
        description="Ordered steps, e.g. mcp:get_customer → llm:synthesis",
    )
    mcp_calls: list[ToolCallDebug] = Field(default_factory=list, alias="mcpCalls")
    rag_calls: list[ToolCallDebug] = Field(default_factory=list, alias="ragCalls")
    llm: LlmDebugInfo | None = None

    model_config = {"populate_by_name": True}


class ChatResponse(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    answer: str
    sources: list[SourceItem] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list, alias="toolsUsed")
    facts: list[FactItem] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    debug: ResponseDebug | None = None

    model_config = {"populate_by_name": True}


class HealthResponse(BaseModel):
    status: str
    service: str = "enterprise-api"


class ReadyResponse(BaseModel):
    status: str
    mcp: str
    rag: str
    llm: str
