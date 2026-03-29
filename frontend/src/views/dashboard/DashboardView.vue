<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchDashboardOverviewApi } from '@/api/dashboard'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { DashboardOverview } from '@/types'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const loading = ref(false)
const overview = ref<DashboardOverview | null>(null)

async function loadData() {
  loading.value = true
  try {
    overview.value = await fetchDashboardOverviewApi()
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <PageHero
      :title="`${authStore.user?.real_name || ''}，欢迎回来`"
      tag="数据概览"
    >
      <el-button plain @click="loadData">刷新数据</el-button>
    </PageHero>

    <div v-if="overview" class="card-grid">
      <StatCard
        v-for="card in overview.cards"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :desc="card.desc"
        :theme="card.theme"
      />
    </div>

    <div v-if="overview" class="dual-grid">
      <section class="panel panel-inner">
        <h3 class="section-title">重点数据</h3>
        <p class="section-subtitle">按当前角色最有展示价值的数据进行聚合展示</p>
        <div class="highlight-list" style="margin-top: 18px">
          <div v-for="item in overview.highlights" :key="`${item.label}-${item.extra}`" class="highlight-item">
            <div>
              <strong>{{ item.label }}</strong>
              <div class="section-subtitle">{{ item.extra || '系统实时统计结果' }}</div>
            </div>
            <div style="font-size: 24px; font-weight: 800">{{ item.value }}</div>
          </div>
        </div>
      </section>

      <section class="panel panel-inner">
        <h3 class="section-title">系统提示</h3>
        <p class="section-subtitle">用于答辩演示的业务说明和状态提示</p>
        <div class="notice-list" style="margin-top: 18px">
          <div v-for="notice in overview.announcements" :key="notice" class="notice-item">
            <span>{{ notice }}</span>
            <el-tag type="primary" effect="plain" round>实时</el-tag>
          </div>
        </div>
      </section>
    </div>

    <EmptyState v-else-if="!loading" title="暂无仪表盘数据" />
  </div>
</template>
