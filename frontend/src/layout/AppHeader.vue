<script setup lang="ts">
import { ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/store/auth'
import { roleLabelMap } from '@/utils/role'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const title = computed(() => route.meta.title || '教学管理系统')
const dateText = computed(() =>
  new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())
)

function handleLogout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <header class="app-header">
    <div>
      <div class="app-header__eyebrow">{{ dateText }}</div>
      <h2>{{ title }}</h2>
    </div>
    <div class="app-header__right">
      <el-tag effect="plain" round size="large">{{ roleLabelMap[authStore.role || 'student'] }}</el-tag>
      <el-dropdown>
        <div class="user-chip">
          <div class="user-chip__avatar">{{ authStore.user?.real_name?.slice(0, 1) || 'U' }}</div>
          <div>
            <div class="user-chip__name">{{ authStore.user?.real_name }}</div>
            <div class="user-chip__account">@{{ authStore.user?.username }}</div>
          </div>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="router.push('/profile')">个人信息</el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 26px;
}

.app-header__eyebrow {
  color: var(--color-subtitle);
  font-size: 13px;
}

.app-header h2 {
  margin: 8px 0 0;
  font-size: 28px;
}

.app-header__right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: var(--shadow-card);
  cursor: pointer;
}

.user-chip__avatar {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--color-primary), #60a5fa);
  color: #fff;
  font-weight: 800;
}

.user-chip__name {
  font-size: 14px;
  font-weight: 700;
}

.user-chip__account {
  color: var(--color-subtitle);
  font-size: 12px;
}

@media (max-width: 860px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 20px 16px;
  }
}
</style>
