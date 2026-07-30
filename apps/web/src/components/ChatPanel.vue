<script setup lang="ts">
import { useChat } from "../composables/useChat";
import BriefingSidebar from "./chat/BriefingSidebar.vue";
import ChatComposer from "./chat/ChatComposer.vue";
import ChatHeader from "./chat/ChatHeader.vue";
import MessageList from "./chat/MessageList.vue";

const { input, loading, error, messages, latest, submit } = useChat();
</script>

<template>
  <section class="chat-panel chat-panel--lumen">
    <div class="chat-panel__main">
      <ChatHeader :loading="loading" />
      <MessageList :messages="messages" :loading="loading" :error="error" />
      <ChatComposer v-model="input" :loading="loading" @submit="submit" />
    </div>
    <BriefingSidebar :latest="latest" />
  </section>
</template>

<style scoped>
.chat-panel--lumen {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 380px);
  height: 100%;
  min-height: 0;
  border: 1px solid var(--lumen-rule);
  border-radius: calc(12px * var(--scale));
  overflow: hidden;
  background:
    radial-gradient(80% 40% at 100% 0%, oklch(76% 0.17 50 / 0.05) 0%, transparent 55%),
    oklch(15% 0.014 265);
  box-shadow: 0 calc(4px * var(--scale)) calc(32px * var(--scale)) oklch(0% 0 0 / 0.45);
}

.chat-panel__main {
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
}

@media (max-width: 820px) {
  .chat-panel--lumen {
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr) auto;
  }
}
</style>
