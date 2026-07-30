<script setup lang="ts">
const input = defineModel<string>({ required: true });

defineProps<{
  loading: boolean;
}>();

const emit = defineEmits<{
  submit: [];
}>();
</script>

<template>
  <form class="composer" @submit.prevent="emit('submit')">
    <label class="composer__label" for="chat-input">Briefing prompt</label>
    <div class="composer__row">
      <input
        id="chat-input"
        v-model="input"
        data-testid="chat-input"
        type="text"
        placeholder="Prepare me for my meeting with ACME"
        :disabled="loading"
        autocomplete="off"
      />
      <button type="submit" data-testid="chat-send" :disabled="loading || !input.trim()">
        {{ loading ? "Working…" : "Send" }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.composer {
  padding:
    calc(18px * var(--scale))
    calc(var(--page-pad-x) * var(--scale))
    calc(var(--page-pad-y) * var(--scale));
  border-top: calc(1px * var(--scale)) solid var(--lumen-rule);
}

.composer__label {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.composer__row {
  display: flex;
  gap: var(--space-xs);
}

.composer__row input {
  flex: 1;
  min-width: 0;
  padding: calc(8px * var(--scale)) calc(12px * var(--scale));
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: var(--lumen-panel);
  font-family: var(--lumen-font-body);
  font-size: var(--text-md);
  color: var(--lumen-ink);
  transition:
    border-color var(--dur-short) var(--ease-out),
    background var(--dur-short) var(--ease-out);
}

.composer__row input::placeholder {
  color: var(--lumen-ink-2);
  opacity: 0.55;
}

.composer__row input:hover:not(:disabled) {
  border-color: oklch(76% 0.17 50 / 0.35);
}

.composer__row input:focus-visible {
  outline: 2px solid var(--lumen-accent);
  outline-offset: 2px;
  border-color: var(--lumen-accent);
}

.composer__row input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.composer__row button {
  flex-shrink: 0;
  padding: calc(8px * var(--scale)) calc(16px * var(--scale));
  border: 1px solid var(--lumen-accent);
  border-radius: var(--radius-sm);
  background: var(--lumen-accent);
  color: oklch(13% 0.014 265);
  font-family: var(--lumen-font-label);
  font-size: calc(10px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  white-space: nowrap;
  transition:
    transform 60ms var(--ease-out),
    background var(--dur-short) var(--ease-out),
    color var(--dur-short) var(--ease-out);
}

.composer__row button:hover:not(:disabled) {
  background: oklch(80% 0.17 50);
  transform: translateY(-1px);
}

.composer__row button:active:not(:disabled) {
  transform: translateY(0);
}

.composer__row button:focus-visible {
  outline: 2px solid var(--lumen-accent);
  outline-offset: 2px;
}

.composer__row button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (prefers-reduced-motion: reduce) {
  .composer__row button:hover:not(:disabled) {
    transform: none;
  }
}

@media (max-width: 820px) {
  .composer {
    padding: var(--space-sm) var(--space-md);
  }
}
</style>
