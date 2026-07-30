export interface SourceItem {
  title: string;
  source: string;
  snippet?: string;
}

export interface ToolCallDebug {
  tool: string;
  source: "mcp" | "rag";
  arguments: Record<string, string>;
  resultPreview: string;
  durationMs?: number;
}

export interface LlmDebugInfo {
  model: string;
  role: string;
  promptTokens: number;
  completionTokens: number;
  note: string;
}

export interface DebugStep {
  id: string;
  kind: "mcp" | "rag" | "llm" | "synthesis";
  title: string;
  inputSummary: string;
  outputSummary: string;
  durationMs?: number;
  raw?: Record<string, unknown>;
}

export interface ResponseDebug {
  steps: DebugStep[];
  pipeline: string[];
  mcpCalls: ToolCallDebug[];
  ragCalls: ToolCallDebug[];
  llm?: LlmDebugInfo;
}

export interface ChatResponse {
  conversationId: string;
  answer: string;
  sources: SourceItem[];
  toolsUsed: string[];
  facts?: Array<{ label: string; value: string }>;
  recommendations?: Array<{ title: string; detail: string }>;
  debug?: ResponseDebug;
}

const API_URL = (
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "")
).replace(/\/$/, "");

export async function sendChat(
  conversationId: string,
  message: string,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversationId, message }),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Chat request failed (${response.status})`);
  }
  return response.json();
}
