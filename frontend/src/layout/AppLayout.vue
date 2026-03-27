<template>
  <div class="app-shell">
    <AppSidebar />
    <div class="app-main">
      <AppHeader />
      <main class="app-content">
        <router-view v-slot="{ Component }">
          <transition name="page-transition" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 284px minmax(0, 1fr);
  min-height: 100vh;
}

.app-main {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.app-content {
  padding: 0 26px 28px;
}

@media (max-width: 1080px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .app-content {
    padding: 0 16px 20px;
  }
}
</style>
