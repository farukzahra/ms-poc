export interface SourceItem {
  title: string;
  source: string;
  snippet?: string;
}

export interface ChatResponse {
  conversationId: string;
  answer: string;
  sources: SourceItem[];
  toolsUsed: string[];
  facts?: Array<{ label: string; value: string }>;
  recommendations?: Array<{ title: string; detail: string }>;
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
