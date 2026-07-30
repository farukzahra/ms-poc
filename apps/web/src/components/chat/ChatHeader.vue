<script setup lang="ts">
defineProps<{
  loading: boolean;
}>();
</script>

<template>
  <header class="chat-header">
    <div class="chat-header__copy">
      <h1>Enterprise AI Sales Intelligence</h1>
      <p class="chat-header__eyebrow">Executive briefing agent</p>
      <p class="chat-header__lede">Ask about ACME, Globex, or Initech for an executive briefing.</p>
    </div>
    <div class="chat-header__status" aria-live="polite">
      <span class="status-dot" :class="{ active: loading }" aria-hidden="true" />
      <span>{{ loading ? "Synthesizing briefing…" : "Ready" }}</span>
    </div>
  </header>
</template>

<style scoped>
.chat-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: calc(18px * var(--scale));
  padding:
    calc(var(--page-pad-y) * var(--scale))
    calc(var(--page-pad-x) * var(--scale))
    calc(18px * var(--scale));
  border-bottom: calc(1px * var(--scale)) solid var(--lumen-rule);
}

.chat-header__copy h1 {
  margin: 0;
  font-family: var(--lumen-font-display);
  font-size: var(--text-xl);
  font-weight: 400;
  font-style: normal;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--lumen-ink);
  overflow-wrap: anywhere;
  min-width: 0;
}

.chat-header__eyebrow {
  margin: calc(6px * var(--scale)) 0 0;
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lumen-accent);
}

.chat-header__lede {
  margin: calc(8px * var(--scale)) 0 0;
  font-size: var(--text-sm);
  color: var(--lumen-ink-2);
  max-width: 42ch;
}

.chat-header__status {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--lumen-ink-2);
  white-space: nowrap;
  flex-shrink: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--lumen-rule);
  transition: background var(--dur-short) var(--ease-out);
}

.status-dot.active {
  background: var(--lumen-accent);
  box-shadow: 0 0 0 1px var(--lumen-accent);
}

@media (max-width: 820px) {
  .chat-header {
    flex-direction: column;
    padding: var(--space-sm) var(--space-md);
  }

  .chat-header__status {
    align-self: flex-start;
  }
}
</style>
