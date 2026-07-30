<script setup lang="ts">
import { ref } from "vue";
import { sendChat, type ChatResponse, type SourceItem } from "../api/client";

const conversationId = crypto.randomUUID();
const input = ref("");
const loading = ref(false);
const error = ref("");
const messages = ref<Array<{ role: "user" | "assistant"; content: string }>>([]);
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
    messages.value.push({ role: "assistant", content: response.answer });
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

function isFactLine(line: string): boolean {
  return line.includes("## FACT") || line.startsWith("- ");
}

function isRecommendationLine(line: string): boolean {
  return line.includes("## RECOMMENDATION") || line.startsWith("- **");
}
</script>

<template>
  <section class="chat-panel">
    <header>
      <h1>Enterprise AI Sales Intelligence</h1>
      <p>Ask about ACME, Globex, or Initech for an executive briefing.</p>
    </header>

    <div class="messages" data-testid="messages">
      <article
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <strong>{{ message.role === "user" ? "You" : "Agent" }}</strong>
        <pre>{{ message.content }}</pre>
      </article>
      <p v-if="loading" class="loading">
        Thinking… Azure responses can take up to 60 seconds.
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <form @submit.prevent="submit" class="composer">
      <input
        v-model="input"
        data-testid="chat-input"
        placeholder="Prepare me for my meeting with ACME"
        :disabled="loading"
      />
      <button type="submit" data-testid="chat-send" :disabled="loading">Send</button>
    </form>

    <aside v-if="latest" class="meta">
      <section v-if="latest.toolsUsed.length">
        <h2>Tools used</h2>
        <ul>
          <li v-for="tool in latest.toolsUsed" :key="tool">{{ tool }}</li>
        </ul>
      </section>
      <section v-if="latest.sources.length">
        <h2>Sources</h2>
        <ul>
          <li v-for="source in latest.sources" :key="source.source">
            <strong>{{ source.title }}</strong>
            <span>{{ source.source }}</span>
            <p v-if="source.snippet">{{ source.snippet }}</p>
          </li>
        </ul>
      </section>
      <section v-if="latest.recommendations?.length">
        <h2>Recommendations</h2>
        <ul>
          <li v-for="item in latest.recommendations" :key="item.title">
            <strong>{{ item.title }}</strong> — {{ item.detail }}
          </li>
        </ul>
      </section>
    </aside>
  </section>
</template>
