<script setup lang="ts">
import { computed } from "vue";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const props = defineProps<{
  messages: ChatMessage[];
  loading: boolean;
  error: string;
}>();

interface ContentBlock {
  kind: "heading" | "fact" | "recommendation" | "text";
  text: string;
}

function parseContent(content: string): ContentBlock[] {
  const blocks: ContentBlock[] = [];
  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    if (line.startsWith("# ")) {
      blocks.push({ kind: "heading", text: line.slice(2) });
    } else if (
      line.includes("## FACT") ||
      (line.startsWith("- ") && !line.startsWith("- **"))
    ) {
      blocks.push({ kind: "fact", text: line.replace(/^## FACT\s*/i, "").replace(/^-\s*/, "") });
    } else if (line.includes("## RECOMMENDATION") || line.startsWith("- **")) {
      blocks.push({
        kind: "recommendation",
        text: line.replace(/^## RECOMMENDATION\s*/i, "").replace(/^-\s*\*\*/, "").replace(/\*\*$/, ""),
      });
    } else {
      blocks.push({ kind: "text", text: line });
    }
  }
  return blocks;
}

const parsedMessages = computed(() =>
  props.messages.map((message) => ({
    ...message,
    blocks: message.role === "assistant" ? parseContent(message.content) : null,
  })),
);
</script>

<template>
  <div class="message-list" data-testid="messages">
    <p v-if="messages.length === 0" class="message-list__empty">
      Start with a customer name — the agent pulls CRM, sales, tickets, and documents.
    </p>

    <article
      v-for="(message, index) in parsedMessages"
      :key="index"
      :class="['message', message.role]"
    >
      <header class="message__meta">
        <span class="message__role">{{ message.role === "user" ? "You" : "Agent" }}</span>
      </header>

      <div v-if="message.role === 'user'" class="message__body">
        {{ message.content }}
      </div>

      <div v-else class="message__body message__body--structured">
        <template v-for="(block, blockIndex) in message.blocks" :key="blockIndex">
          <h3 v-if="block.kind === 'heading'" class="block-heading">{{ block.text }}</h3>
          <p v-else-if="block.kind === 'fact'" class="block-fact">
            <span class="block-label">Fact</span>
            {{ block.text }}
          </p>
          <p v-else-if="block.kind === 'recommendation'" class="block-rec">
            <span class="block-label">Recommendation</span>
            {{ block.text }}
          </p>
          <p v-else class="block-text">{{ block.text }}</p>
        </template>
      </div>
    </article>

    <p v-if="loading" class="message-list__loading">
      Thinking… Azure responses can take up to 60 seconds.
    </p>
    <p v-if="error" class="message-list__error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: 0 calc(var(--page-pad-x) * var(--scale)) var(--space-md);
  min-height: 0;
}

.message-list__empty {
  margin: auto;
  max-width: 36ch;
  text-align: center;
  color: var(--lumen-ink-2);
  font-size: var(--text-sm);
  line-height: 1.55;
  opacity: 0.75;
}

.message {
  max-width: 52ch;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-md);
  background: var(--lumen-panel);
  transition:
    transform var(--dur-short) var(--ease-out),
    border-color var(--dur-short) var(--ease-out);
}

.message.user {
  align-self: flex-end;
  border-color: oklch(76% 0.17 50 / 0.25);
  background: oklch(17% 0.016 265 / 0.85);
}

.message.assistant {
  align-self: flex-start;
  max-width: min(52ch, 100%);
}

.message.assistant:hover {
  border-color: oklch(76% 0.17 50 / 0.2);
}

.message__meta {
  margin-bottom: var(--space-2xs);
}

.message__role {
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lumen-accent);
}

.message.user .message__role {
  color: var(--lumen-ink-2);
}

.message__body {
  font-size: var(--text-md);
  line-height: 1.55;
  color: var(--lumen-ink-2);
  overflow-wrap: anywhere;
  min-width: 0;
}

.block-heading {
  margin: 0 0 var(--space-xs);
  font-family: var(--lumen-font-display);
  font-size: var(--text-lg);
  font-weight: 400;
  font-style: normal;
  color: var(--lumen-ink);
}

.block-fact,
.block-rec,
.block-text {
  margin: var(--space-2xs) 0;
}

.block-label {
  display: inline-block;
  margin-right: var(--space-2xs);
  padding: 2px var(--space-2xs);
  border-radius: var(--radius-sm);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.block-fact .block-label {
  background: oklch(76% 0.17 50 / 0.12);
  color: var(--lumen-accent);
}

.block-rec .block-label {
  background: oklch(68% 0.16 18 / 0.12);
  color: var(--lumen-error);
}

.message-list__loading {
  font-size: var(--text-sm);
  color: var(--lumen-ink-2);
  font-family: var(--lumen-font-label);
  letter-spacing: 0.04em;
}

.message-list__error {
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  border: 1px solid oklch(68% 0.16 18 / 0.35);
  background: oklch(68% 0.16 18 / 0.08);
  color: var(--lumen-error);
  font-size: var(--text-sm);
}
</style>
