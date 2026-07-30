<script setup lang="ts">
import type { ChatResponse } from "../../api/client";

defineProps<{
  latest: ChatResponse | null;
}>();
</script>

<template>
  <aside v-if="latest" class="briefing-sidebar">
    <section class="panel panel--legend">
      <h2>Briefing</h2>
      <p class="panel__note">
        <span class="badge badge--fact">Fact</span> verified tool/document data ·
        <span class="badge badge--rec">AI recommendation</span> LLM-suggested actions.
        Use <strong>Debug</strong> under agent messages for the pipeline.
      </p>
    </section>

    <section v-if="latest.toolsUsed.length" class="panel">
      <h2>Tools used</h2>
      <ul class="chip-list">
        <li v-for="tool in latest.toolsUsed" :key="tool">{{ tool }}</li>
      </ul>
    </section>

    <section v-if="latest.sources.length" class="panel">
      <h2>Document sources</h2>
      <ul class="source-list">
        <li v-for="source in latest.sources" :key="source.source" class="source-card">
          <strong>{{ source.title }}</strong>
          <span class="source-path">{{ source.source }}</span>
          <p v-if="source.snippet">{{ source.snippet }}</p>
        </li>
      </ul>
    </section>

    <section v-if="latest.facts?.length" class="panel panel--facts">
      <header class="panel__header">
        <h2>Facts</h2>
        <span class="badge badge--fact">Verified data</span>
      </header>
      <dl class="fact-grid">
        <template v-for="fact in latest.facts" :key="fact.label">
          <dt>{{ fact.label }}</dt>
          <dd>{{ fact.value }}</dd>
        </template>
      </dl>
    </section>

    <section v-if="latest.recommendations?.length" class="panel panel--rec">
      <header class="panel__header">
        <h2>Recommendations</h2>
        <span class="badge badge--rec">LLM guidance</span>
      </header>
      <ul class="rec-list">
        <li v-for="item in latest.recommendations" :key="item.title" class="rec-card">
          <strong>{{ item.title }}</strong>
          <span>{{ item.detail }}</span>
        </li>
      </ul>
    </section>
  </aside>

  <aside v-else class="briefing-sidebar briefing-sidebar--empty">
    <p>
      After your first response, verified facts, document sources, and recommendations appear here.
    </p>
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
  width: 100%;
  margin-bottom: calc(18px * var(--scale));
  padding-bottom: calc(18px * var(--scale));
  border-bottom: calc(1px * var(--scale)) solid var(--lumen-rule);
}

.panel:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.panel--legend {
  padding: var(--space-sm);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(11% 0.012 265 / 0.55);
}

.panel--facts {
  border-left: 3px solid oklch(76% 0.17 50 / 0.45);
  padding-left: var(--space-sm);
}

.panel--rec {
  border-left: 3px solid oklch(68% 0.16 18 / 0.45);
  padding-left: var(--space-sm);
}

.panel__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2xs);
  margin-bottom: var(--space-xs);
}

.panel h2 {
  margin: 0;
  font-family: var(--lumen-font-label);
  font-size: calc(10px * var(--scale));
  font-weight: 500;
  font-style: normal;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lumen-accent);
}

.panel__note {
  margin: var(--space-xs) 0 0;
  font-size: var(--text-xs);
  line-height: 1.5;
  color: var(--lumen-ink-2);
}

.badge {
  display: inline-block;
  padding: 2px var(--space-2xs);
  border-radius: var(--radius-sm);
  font-family: var(--lumen-font-label);
  font-size: calc(8px * var(--scale));
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.badge--fact {
  background: oklch(76% 0.17 50 / 0.14);
  color: var(--lumen-accent);
}

.badge--rec {
  background: oklch(68% 0.16 18 / 0.14);
  color: var(--lumen-error);
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
  width: 100%;
}

.source-card,
.rec-card {
  padding: var(--space-xs);
  border: 1px solid var(--lumen-rule);
  border-radius: var(--radius-sm);
  background: oklch(13% 0.014 265 / 0.5);
  font-size: var(--text-xs);
  line-height: 1.45;
  color: var(--lumen-ink-2);
}

.rec-card {
  border-color: oklch(68% 0.16 18 / 0.2);
  background: oklch(68% 0.16 18 / 0.06);
}

.source-list strong,
.rec-list strong {
  display: block;
  font-family: var(--lumen-font-display);
  font-weight: 400;
  color: var(--lumen-ink);
  margin-bottom: 2px;
}

.source-path {
  display: block;
  font-family: var(--lumen-font-label);
  color: var(--lumen-accent);
  margin-top: 2px;
  font-size: calc(9px * var(--scale));
  word-break: break-word;
}

.fact-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
  gap: var(--space-2xs) var(--space-xs);
  margin: 0;
  width: 100%;
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
