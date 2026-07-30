<script setup lang="ts">
import ChatPanel from "./components/ChatPanel.vue";
import { useLumenTheme } from "./composables/useLumenTheme";

useLumenTheme();
</script>

<template>
  <div class="app">
    <main class="app-main">
      <ChatPanel />
    </main>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  min-height: 100dvh;
}

.app-main {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding:
    calc(var(--page-pad-y) * var(--scale))
    calc(var(--page-pad-x) * var(--scale));
}
</style>
