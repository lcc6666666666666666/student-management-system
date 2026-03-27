<script setup lang="ts">
defineProps<{
  title: string
  description: string
  tag?: string
}>()
</script>

<template>
  <section class="page-hero panel">
    <div class="page-hero__content">
      <div v-if="tag" class="page-hero__tag">{{ tag }}</div>
      <h1>{{ title }}</h1>
      <p>{{ description }}</p>
    </div>
    <div class="page-hero__actions">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.page-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(248, 251, 255, 0.9));
}

.page-hero__content {
  max-width: 680px;
}

.page-hero__tag {
  display: inline-flex;
  align-items: center;
  padding: 7px 12px;
  border-radius: 999px;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.page-hero h1 {
  margin: 16px 0 10px;
  font-size: 30px;
  line-height: 1.2;
}

.page-hero p {
  margin: 0;
  color: var(--color-subtitle);
  line-height: 1.7;
}

.page-hero__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 920px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
