<script setup lang="ts">
import { computed } from "vue";
import type { ChatMessage } from "../../composables/useChat";
import MessageDebug from "./MessageDebug.vue";
import {
  factGridItems,
  parseBriefing,
  splitRecommendationBullet,
  type BriefingBlock,
} from "./parseBriefing";

const props = defineProps<{
  messages: ChatMessage[];
  loading: boolean;
  error: string;
}>();

function isFactGrid(blocks: BriefingBlock[]): boolean {
  const bullets = blocks.filter((block) => block.kind === "bullet");
  if (bullets.length === 0) return false;
  return factGridItems(blocks).length === bullets.length;
}

const parsedMessages = computed(() =>
  props.messages.map((message) => ({
    ...message,
    parsed: message.role === "assistant" ? parseBriefing(message.content) : null,
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

      <div
        v-else-if="message.parsed?.hasStructure"
        class="message__body message__body--structured"
      >
        <h3 v-if="message.parsed.title" class="briefing-title">
          {{ message.parsed.title }}
        </h3>

        <section v-if="message.parsed.facts" class="briefing-section briefing-section--facts">
          <header class="briefing-section__header">
            <h4 class="briefing-section__title">Facts</h4>
            <span class="briefing-section__source">CRM · Sales · Tickets · Documents</span>
          </header>

          <dl
            v-if="isFactGrid(message.parsed.facts.blocks)"
            class="fact-grid"
          >
            <template
              v-for="item in factGridItems(message.parsed.facts.blocks)"
              :key="item.label + item.value"
            >
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </template>
          </dl>

          <div v-else class="section-body">
            <template v-for="(block, blockIndex) in message.parsed.facts.blocks" :key="blockIndex">
              <h5 v-if="block.kind === 'subheading'" class="block-subheading">{{ block.text }}</h5>
              <p v-else-if="block.kind === 'text'" class="block-text">{{ block.text }}</p>
              <ul v-else-if="block.kind === 'bullet'" class="block-list">
                <li>{{ block.text }}</li>
              </ul>
              <ol
                v-else-if="block.kind === 'numbered'"
                class="block-list block-list--numbered"
                :start="block.order"
              >
                <li>{{ block.text }}</li>
              </ol>
            </template>
          </div>
        </section>

        <section
          v-if="message.parsed.recommendations"
          class="briefing-section briefing-section--rec"
        >
          <header class="briefing-section__header">
            <h4 class="briefing-section__title">AI Recommendations</h4>
            <span class="briefing-section__source">Suggested next steps · review before acting</span>
          </header>

          <div class="section-body">
            <template
              v-for="(block, blockIndex) in message.parsed.recommendations.blocks"
              :key="blockIndex"
            >
              <h5 v-if="block.kind === 'subheading'" class="block-subheading block-subheading--rec">
                {{ block.text }}
              </h5>
              <p v-else-if="block.kind === 'text'" class="block-text block-text--rec">{{ block.text }}</p>
              <div
                v-else-if="block.kind === 'bullet'"
                class="rec-item"
              >
                <strong v-if="splitRecommendationBullet(block.text).title">
                  {{ splitRecommendationBullet(block.text).title }}
                </strong>
                <p>{{ splitRecommendationBullet(block.text).detail || block.text }}</p>
              </div>
              <div v-else-if="block.kind === 'numbered'" class="rec-item rec-item--numbered">
                <span class="rec-item__index">{{ block.order }}</span>
                <p>{{ block.text }}</p>
              </div>
            </template>
          </div>
        </section>

        <MessageDebug v-if="message.debug?.steps?.length" :debug="message.debug" />
      </div>

      <div v-else class="message__body message__body--plain">
        <pre class="message__raw">{{ message.content }}</pre>
        <MessageDebug v-if="message.debug?.steps?.length" :debug="message.debug" />
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
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-md);
  background: var(--lumen-panel);
}

.message.user {
  align-self: flex-end;
  max-width: min(52ch, 88%);
  border-color: oklch(76% 0.17 50 / 0.25);
  background: oklch(17% 0.016 265 / 0.85);
}

.message.assistant {
  align-self: stretch;
  width: 100%;
  max-width: 100%;
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

.message__body--structured {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  width: 100%;
}

.message__body--plain {
  width: 100%;
}

.message__raw {
  margin: 0;
  font-family: inherit;
  font-size: var(--text-sm);
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--lumen-ink-2);
}

.briefing-title {
  margin: 0;
  padding-bottom: var(--space-xs);
  border-bottom: 1px solid var(--lumen-rule);
  font-family: var(--lumen-font-display);
  font-size: var(--text-xl);
  font-weight: 400;
  color: var(--lumen-ink);
}

.briefing-section {
  width: 100%;
  padding: var(--space-md);
  border-radius: var(--radius-md);
}

.briefing-section--facts {
  border: 1px solid oklch(76% 0.17 50 / 0.22);
  background: oklch(76% 0.17 50 / 0.05);
}

.briefing-section--rec {
  border: 1px solid oklch(68% 0.16 18 / 0.28);
  border-left: 4px solid oklch(68% 0.16 18 / 0.75);
  background: oklch(68% 0.16 18 / 0.07);
  box-shadow: 0 0 0 1px oklch(68% 0.16 18 / 0.06);
}

.briefing-section__header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-2xs) var(--space-sm);
  margin-bottom: var(--space-sm);
}

.briefing-section__title {
  margin: 0;
  font-family: var(--lumen-font-label);
  font-size: calc(11px * var(--scale));
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.briefing-section--facts .briefing-section__title {
  color: var(--lumen-accent);
}

.briefing-section--rec .briefing-section__title {
  color: var(--lumen-error);
}

.briefing-section__source {
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--lumen-ink-2);
  opacity: 0.9;
}

.section-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.fact-grid {
  display: grid;
  grid-template-columns: minmax(9rem, 0.85fr) minmax(0, 1.5fr);
  gap: var(--space-xs) var(--space-md);
  margin: 0;
  width: 100%;
}

.fact-grid dt {
  margin: 0;
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--lumen-accent);
}

.fact-grid dd {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--lumen-ink);
}

.block-subheading {
  margin: var(--space-xs) 0 0;
  font-family: var(--lumen-font-display);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--lumen-ink);
}

.block-subheading--rec {
  color: var(--lumen-error);
  opacity: 0.95;
}

.block-text {
  margin: 0;
  font-size: var(--text-sm);
  line-height: 1.55;
  color: var(--lumen-ink-2);
}

.block-text--rec {
  color: var(--lumen-ink);
}

.block-list {
  margin: 0;
  padding-left: 1.2rem;
  font-size: var(--text-sm);
  color: var(--lumen-ink);
}

.rec-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xs);
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  background: oklch(9% 0.01 265 / 0.35);
  border: 1px solid oklch(68% 0.16 18 / 0.15);
}

.rec-item strong {
  font-family: var(--lumen-font-display);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--lumen-ink);
}

.rec-item p {
  margin: 0;
  font-size: var(--text-sm);
  line-height: 1.55;
  color: var(--lumen-ink-2);
}

.rec-item--numbered {
  flex-direction: row;
  align-items: flex-start;
  gap: var(--space-sm);
}

.rec-item__index {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: oklch(68% 0.16 18 / 0.18);
  color: var(--lumen-error);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 600;
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

@media (max-width: 520px) {
  .fact-grid {
    grid-template-columns: 1fr;
  }
}
</style>
