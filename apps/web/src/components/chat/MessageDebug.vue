<script setup lang="ts">
import { ref } from "vue";
import type { DebugStep, ResponseDebug } from "../../api/client";

defineProps<{
  debug: ResponseDebug;
}>();

const expanded = ref(false);
const showRaw = ref<Record<string, boolean>>({});

function kindLabel(kind: DebugStep["kind"]): string {
  switch (kind) {
    case "mcp":
      return "CALL";
    case "rag":
      return "RETRIEVE";
    case "llm":
    case "synthesis":
      return "LLM";
    default:
      return String(kind).toUpperCase();
  }
}

function toggleRaw(stepId: string) {
  showRaw.value = {
    ...showRaw.value,
    [stepId]: !showRaw.value[stepId],
  };
}
</script>

<template>
  <div class="message-debug">
    <button
      type="button"
      class="message-debug__toggle"
      data-testid="debug-toggle"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      {{ expanded ? "Hide debug" : "Debug" }}
      <span v-if="!expanded && debug.steps.length" class="message-debug__count">
        {{ debug.steps.length }} step{{ debug.steps.length === 1 ? "" : "s" }}
      </span>
    </button>

    <div v-if="expanded" class="message-debug__panel" data-testid="debug-panel">
      <p class="message-debug__intro">
        Step-by-step reasoning pipeline. <strong>Facts</strong> come from MCP/RAG steps below;
        <strong>recommendations</strong> are produced in the final LLM synthesis step.
      </p>

      <ol class="message-debug__steps">
        <li
          v-for="(step, index) in debug.steps"
          :key="step.id"
          class="debug-step"
          :data-testid="`debug-step-${index + 1}`"
        >
          <header class="debug-step__header">
            <span class="debug-step__number">{{ index + 1 }}</span>
            <span :class="['debug-step__kind', `debug-step__kind--${step.kind}`]">
              {{ kindLabel(step.kind) }}
            </span>
            <strong class="debug-step__title">{{ step.title }}</strong>
            <span v-if="step.durationMs" class="debug-step__duration">
              {{ step.durationMs.toFixed(1) }} ms
            </span>
          </header>

          <div v-if="step.inputSummary" class="debug-step__row">
            <span class="debug-step__label">Input</span>
            <p class="debug-step__text">{{ step.inputSummary }}</p>
          </div>

          <div v-if="step.outputSummary" class="debug-step__row">
            <span class="debug-step__label">Output</span>
            <p class="debug-step__text">{{ step.outputSummary }}</p>
          </div>

          <button
            v-if="step.raw"
            type="button"
            class="debug-step__raw-toggle"
            @click="toggleRaw(step.id)"
          >
            {{ showRaw[step.id] ? "Hide raw data" : "Show raw data" }}
          </button>
          <pre v-if="step.raw && showRaw[step.id]" class="debug-step__raw">{{
            JSON.stringify(step.raw, null, 2)
          }}</pre>
        </li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.message-debug {
  margin-top: var(--space-sm);
  padding-top: var(--space-xs);
  border-top: 1px solid var(--lumen-rule);
}

.message-debug__toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2xs);
  padding: var(--space-2xs) var(--space-xs);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(13% 0.014 265 / 0.5);
  color: var(--lumen-ink-2);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition:
    border-color var(--dur-short) var(--ease-out),
    color var(--dur-short) var(--ease-out);
}

.message-debug__toggle:hover {
  border-color: oklch(76% 0.17 50 / 0.35);
  color: var(--lumen-accent);
}

.message-debug__count {
  color: var(--lumen-accent);
  font-weight: 400;
}

.message-debug__panel {
  margin-top: var(--space-xs);
  padding: var(--space-sm);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(11% 0.012 265 / 0.6);
}

.message-debug__intro {
  margin: 0 0 var(--space-sm);
  font-size: var(--text-xs);
  line-height: 1.45;
  color: var(--lumen-ink-2);
}

.message-debug__steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.debug-step {
  padding: var(--space-xs);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(13% 0.014 265 / 0.5);
}

.debug-step__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2xs);
  margin-bottom: var(--space-2xs);
}

.debug-step__number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: oklch(76% 0.17 50 / 0.15);
  color: var(--lumen-accent);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 600;
}

.debug-step__kind {
  padding: 2px var(--space-2xs);
  border-radius: var(--radius-sm);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 600;
  letter-spacing: 0.08em;
}

.debug-step__kind--mcp {
  background: oklch(76% 0.17 50 / 0.12);
  color: var(--lumen-accent);
}

.debug-step__kind--rag {
  background: oklch(76% 0.17 50 / 0.08);
  color: var(--lumen-accent);
}

.debug-step__kind--llm,
.debug-step__kind--synthesis {
  background: oklch(68% 0.16 18 / 0.12);
  color: var(--lumen-error);
}

.debug-step__title {
  flex: 1;
  min-width: 0;
  font-size: var(--text-xs);
  color: var(--lumen-ink);
  font-weight: 500;
}

.debug-step__duration {
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  color: var(--lumen-ink-2);
}

.debug-step__row {
  margin-top: var(--space-2xs);
}

.debug-step__label {
  display: block;
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--lumen-accent);
  margin-bottom: 2px;
}

.debug-step__text {
  margin: 0;
  font-size: var(--text-xs);
  line-height: 1.45;
  color: var(--lumen-ink-2);
  overflow-wrap: anywhere;
}

.debug-step__raw-toggle {
  margin-top: var(--space-2xs);
  padding: 0;
  border: none;
  background: none;
  color: var(--lumen-ink-2);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  text-decoration: underline;
  cursor: pointer;
}

.debug-step__raw-toggle:hover {
  color: var(--lumen-accent);
}

.debug-step__raw {
  margin: var(--space-2xs) 0 0;
  padding: var(--space-2xs);
  border-radius: var(--radius-sm);
  background: oklch(9% 0.01 265 / 0.8);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--lumen-ink-2);
  max-height: 12rem;
  overflow-y: auto;
}
</style>
