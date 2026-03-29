<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="empty-state panel empty-wrap">
    <h3>{{ title }}</h3>
    <p v-if="description">{{ description }}</p>
    <slot />
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 10px;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  color: var(--color-subtitle);
}
</style>
