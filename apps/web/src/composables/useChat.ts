import { ref } from "vue";
import { sendChat, type ChatResponse, type ResponseDebug } from "../api/client";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  debug?: ResponseDebug;
}

export function useChat() {
  const conversationId = crypto.randomUUID();
  const input = ref("");
  const loading = ref(false);
  const error = ref("");
  const messages = ref<ChatMessage[]>([]);
  const latest = ref<ChatResponse | null>(null);

  async function submit() {
    const text = input.value.trim();
    if (!text || loading.value) return;
    error.value = "";
    loading.value = true;
    messages.value.push({ role: "user", content: text });
    input.value = "";
    try {
      const response = await sendChat(
        conversationId,
        text,
        AbortSignal.timeout(120_000),
      );
      latest.value = response;
      messages.value.push({
        role: "assistant",
        content: response.answer,
        debug: response.debug,
      });
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
    } finally {
      loading.value = false;
    }
  }

  return { input, loading, error, messages, latest, submit };
}
