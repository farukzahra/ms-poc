<script setup lang="ts">
import type { ChatResponse } from "../../api/client";

defineProps<{
  latest: ChatResponse | null;
}>();
</script>

<template>
  <aside v-if="latest" class="briefing-sidebar">
    <section v-if="latest.debug" class="panel provenance" data-testid="provenance">
      <h2>Data provenance</h2>
      <p class="panel__note">
        FACT lines come from MCP (CRM, sales, tickets) and RAG (documents).
        RECOMMENDATION is synthesized by the LLM.
      </p>

      <div v-if="latest.debug.pipeline.length" class="pipeline">
        <span class="pipeline__label">Pipeline</span>
        <code>{{ latest.debug.pipeline.join(" → ") }}</code>
      </div>

      <div v-if="latest.debug.mcpCalls.length" class="call-group">
        <h3>
          <span class="badge badge--mcp">MCP</span>
          Structured data
        </h3>
        <article
          v-for="call in latest.debug.mcpCalls"
          :key="call.tool + JSON.stringify(call.arguments)"
          class="call"
        >
          <header class="call__header">
            <strong>{{ call.tool }}</strong>
            <span v-if="call.durationMs">{{ call.durationMs }} ms</span>
          </header>
          <p v-if="Object.keys(call.arguments).length" class="call__args">
            {{ JSON.stringify(call.arguments) }}
          </p>
          <pre v-if="call.resultPreview" class="call__preview">{{ call.resultPreview }}</pre>
        </article>
      </div>

      <div v-if="latest.debug.ragCalls.length" class="call-group">
        <h3>
          <span class="badge badge--rag">RAG</span>
          Document retrieval
        </h3>
        <article
          v-for="call in latest.debug.ragCalls"
          :key="call.tool + call.arguments.query"
          class="call"
        >
          <header class="call__header">
            <strong>{{ call.tool }}</strong>
            <span v-if="call.durationMs">{{ call.durationMs }} ms</span>
          </header>
          <p v-if="Object.keys(call.arguments).length" class="call__args">
            {{ JSON.stringify(call.arguments) }}
          </p>
          <pre v-if="call.resultPreview" class="call__preview">{{ call.resultPreview }}</pre>
        </article>
      </div>

      <div v-if="latest.debug.llm" class="call-group">
        <h3>
          <span class="badge badge--llm">LLM</span>
          Synthesis
        </h3>
        <article class="call">
          <p><strong>Model:</strong> {{ latest.debug.llm.model }}</p>
          <p>
            Tokens: {{ latest.debug.llm.promptTokens }} prompt /
            {{ latest.debug.llm.completionTokens }} completion
          </p>
          <p class="call__note">{{ latest.debug.llm.note }}</p>
        </article>
      </div>
    </section>

    <section v-if="latest.toolsUsed.length" class="panel">
      <h2>Tools used</h2>
      <ul class="chip-list">
        <li v-for="tool in latest.toolsUsed" :key="tool">{{ tool }}</li>
      </ul>
    </section>

    <section v-if="latest.sources.length" class="panel">
      <h2>Sources</h2>
      <ul class="source-list">
        <li v-for="source in latest.sources" :key="source.source">
          <strong>{{ source.title }}</strong>
          <span class="source-path">{{ source.source }}</span>
          <p v-if="source.snippet">{{ source.snippet }}</p>
        </li>
      </ul>
    </section>

    <section v-if="latest.facts?.length" class="panel">
      <h2>Facts</h2>
      <dl class="fact-grid">
        <template v-for="fact in latest.facts" :key="fact.label">
          <dt>{{ fact.label }}</dt>
          <dd>{{ fact.value }}</dd>
        </template>
      </dl>
    </section>

    <section v-if="latest.recommendations?.length" class="panel">
      <h2>Recommendations</h2>
      <ul class="rec-list">
        <li v-for="item in latest.recommendations" :key="item.title">
          <strong>{{ item.title }}</strong>
          <span>{{ item.detail }}</span>
        </li>
      </ul>
    </section>
  </aside>

  <aside v-else class="briefing-sidebar briefing-sidebar--empty">
    <p>Briefing metadata, sources, and provenance appear here after the first response.</p>
  </aside>
</template>

<style scoped>
.briefing-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: calc(var(--page-pad-y) * var(--scale)) calc(var(--page-pad-x) * var(--scale));
  border-left: calc(1px * var(--scale)) solid var(--lumen-rule);
  background:
    radial-gradient(60% 30% at 0% 0%, oklch(76% 0.17 50 / 0.06) 0%, transparent 50%),
    var(--lumen-panel);
  overflow-y: auto;
  min-height: 0;
}

.briefing-sidebar--empty {
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--lumen-ink-2);
  font-size: var(--text-sm);
  line-height: 1.55;
  opacity: 0.75;
}

.panel {
  margin-bottom: calc(18px * var(--scale));
  padding-bottom: calc(18px * var(--scale));
  border-bottom: calc(1px * var(--scale)) solid var(--lumen-rule);
}

.panel:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.panel h2 {
  margin: 0 0 var(--space-xs);
  font-family: var(--lumen-font-label);
  font-size: calc(10px * var(--scale));
  font-weight: 500;
  font-style: normal;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lumen-accent);
}

.panel__note {
  margin: 0 0 var(--space-sm);
  font-size: var(--text-xs);
  line-height: 1.5;
  color: var(--lumen-ink-2);
}

.pipeline {
  margin-bottom: var(--space-sm);
}

.pipeline__label {
  display: block;
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--lumen-accent);
  margin-bottom: var(--space-2xs);
}

.pipeline code {
  display: block;
  padding: var(--space-2xs) var(--space-xs);
  border-radius: var(--radius-sm);
  border: 1px solid var(--lumen-rule);
  background: oklch(13% 0.014 265 / 0.6);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  word-break: break-word;
  color: var(--lumen-ink-2);
}

.call-group {
  margin-top: var(--space-sm);
}

.call-group h3 {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
  margin: 0 0 var(--space-2xs);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--lumen-ink);
}

.badge {
  display: inline-block;
  padding: 2px var(--space-2xs);
  border-radius: var(--radius-sm);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.badge--mcp {
  background: oklch(76% 0.17 50 / 0.12);
  color: var(--lumen-accent);
}

.badge--rag {
  background: oklch(76% 0.17 50 / 0.08);
  color: var(--lumen-accent);
}

.badge--llm {
  background: oklch(68% 0.16 18 / 0.12);
  color: var(--lumen-error);
}

.call {
  margin-top: var(--space-2xs);
  padding: var(--space-xs);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(13% 0.014 265 / 0.5);
  font-size: var(--text-xs);
  transition: border-color var(--dur-short) var(--ease-out);
}

.call:hover {
  border-color: oklch(76% 0.17 50 / 0.25);
}

.call__header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2xs);
  font-family: var(--lumen-font-label);
  color: var(--lumen-accent);
}

.call__args {
  margin: var(--space-2xs) 0 0;
  color: var(--lumen-ink-2);
  word-break: break-word;
}

.call__preview {
  margin: var(--space-2xs) 0 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  color: var(--lumen-ink-2);
}

.call__note {
  margin: var(--space-2xs) 0 0;
  color: var(--lumen-ink-2);
  line-height: 1.45;
}

.chip-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2xs);
}

.chip-list li {
  padding: 2px var(--space-2xs);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-pill);
  background: oklch(76% 0.17 50 / 0.08);
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  color: var(--lumen-ink-2);
}

.source-list,
.rec-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.source-list li,
.rec-list li {
  font-size: var(--text-xs);
  line-height: 1.45;
  color: var(--lumen-ink-2);
}

.source-list strong,
.rec-list strong {
  font-family: var(--lumen-font-display);
  font-weight: 400;
  color: var(--lumen-ink);
}

.source-path {
  display: block;
  font-family: var(--lumen-font-label);
  color: var(--lumen-accent);
  margin-top: 2px;
  font-size: calc(9px * var(--scale));
}

.fact-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
  gap: var(--space-2xs) var(--space-xs);
  margin: 0;
  font-size: var(--text-xs);
}

.fact-grid dt {
  font-family: var(--lumen-font-label);
  font-size: calc(9px * var(--scale));
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--lumen-ink-2);
}

.fact-grid dd {
  margin: 0;
  font-family: var(--lumen-font-label);
  color: var(--lumen-ink);
  overflow-wrap: anywhere;
}

@media (max-width: 820px) {
  .briefing-sidebar {
    border-left: none;
    border-top: calc(1px * var(--scale)) solid var(--lumen-rule);
    max-height: 40vh;
  }
}
</style>
