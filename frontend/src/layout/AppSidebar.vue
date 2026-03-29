<script setup lang="ts">
import {
  Calendar,
  DataLine,
  EditPen,
  HomeFilled,
  Management,
  Notebook,
  Reading,
  Tickets,
  User,
  UserFilled
} from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { getMenuRoutes } from '@/router'
import { useAuthStore } from '@/store/auth'
import { roleLabelMap } from '@/utils/role'

const route = useRoute()
const authStore = useAuthStore()

const iconMap = {
  HomeFilled,
  UserFilled,
  Tickets,
  Notebook,
  Calendar,
  DataLine,
  Reading,
  EditPen,
  Management,
  User
}

const menus = computed(() => getMenuRoutes(authStore.role))
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__panel">
      <div class="brand">
        <div class="brand__logo">TM</div>
        <div>
          <div class="brand__title">教学管理系统</div>
          <div class="brand__sub">{{ roleLabelMap[authStore.role || 'student'] }}工作台</div>
        </div>
      </div>

      <el-menu :default-active="route.path" router class="sidebar__menu">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon>
            <component :is="iconMap[item.meta?.icon as keyof typeof iconMap]" />
          </el-icon>
          <span>{{ item.meta?.title }}</span>
        </el-menu-item>
      </el-menu>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  padding: 20px;
}

.sidebar__panel {
  position: sticky;
  top: 20px;
  display: flex;
  min-height: calc(100vh - 40px);
  flex-direction: column;
  padding: 22px;
  border-radius: 30px;
  background:
    radial-gradient(circle at top, rgba(37, 99, 235, 0.18), transparent 28%),
    linear-gradient(180deg, rgba(12, 20, 39, 0.96), rgba(15, 23, 42, 0.98));
  box-shadow: 0 26px 60px rgba(15, 23, 42, 0.22);
  color: #fff;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 28px;
}

.brand__logo {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #5b8cff, #83d4ff);
  color: #0f172a;
  font-weight: 800;
}

.brand__title {
  font-size: 18px;
  font-weight: 800;
}

.brand__sub {
  margin-top: 4px;
  color: rgba(255, 255, 255, 0.64);
  font-size: 12px;
}

.sidebar__menu {
  flex: 1;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.72);
}

:deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

@media (max-width: 1080px) {
  .sidebar {
    padding: 16px 16px 0;
  }

  .sidebar__panel {
    position: static;
    min-height: auto;
  }
}
</style>
