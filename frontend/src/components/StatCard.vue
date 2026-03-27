<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  desc: string
  theme?: 'primary' | 'emerald' | 'amber' | 'violet'
}>()
</script>

<template>
  <div class="stat-card" :class="`is-${theme || 'primary'}`">
    <div class="stat-card__badge" />
    <div class="stat-card__label">{{ title }}</div>
    <div class="stat-card__value">{{ value }}</div>
    <div class="stat-card__desc">{{ desc }}</div>
  </div>
</template>

<style scoped>
.stat-card {
  position: relative;
  overflow: hidden;
  min-height: 150px;
  padding: 22px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(255, 255, 255, 0.82);
}

.stat-card__badge {
  position: absolute;
  inset: -30px auto auto -20px;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  opacity: 0.18;
}

.stat-card__label {
  position: relative;
  color: var(--color-subtitle);
  font-size: 13px;
}

.stat-card__value {
  position: relative;
  margin-top: 16px;
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -1px;
}

.stat-card__desc {
  position: relative;
  margin-top: 10px;
  color: var(--color-subtitle);
  font-size: 13px;
  line-height: 1.6;
}

.is-primary .stat-card__badge {
  background: var(--color-primary);
}

.is-emerald .stat-card__badge {
  background: var(--color-emerald);
}

.is-amber .stat-card__badge {
  background: var(--color-amber);
}

.is-violet .stat-card__badge {
  background: var(--color-violet);
}
</style>
