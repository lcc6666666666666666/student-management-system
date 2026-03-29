<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, ref } from 'vue'

import { dropCourseApi, fetchStudentCoursesApi } from '@/api/student'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { StudentCourseItem } from '@/types'
import { getStatusLabel } from '@/utils/role'

const loading = ref(false)
const items = ref<StudentCourseItem[]>([])

const stats = computed(() => {
  const total = items.value.length
  const pending = items.value.filter((item) => item.score == null).length
  const graded = items.value.filter((item) => item.score != null).length
  const credits = items.value.reduce((sum, item) => sum + item.credit, 0)
  return { total, pending, graded, credits: credits.toFixed(1) }
})

async function loadData() {
  loading.value = true
  try {
    const data = await fetchStudentCoursesApi()
    items.value = data.items
  } finally {
    loading.value = false
  }
}

async function handleDrop(item: StudentCourseItem) {
  await ElMessageBox.confirm(`确认退掉《${item.course_name}》吗？`, '退课确认', { type: 'warning' })
  await dropCourseApi(item.course_id)
  ElMessage.success('退课成功')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-view">
    <PageHero
      title="我的课程"
      tag="学生端"
    />

    <div class="card-grid">
      <StatCard title="已选课程" :value="stats.total" desc="当前账号已完成选课的课程数量" theme="primary" />
      <StatCard title="待出成绩" :value="stats.pending" desc="尚未录入成绩的课程数量" theme="emerald" />
      <StatCard title="已出成绩" :value="stats.graded" desc="成绩已录入课程数量" theme="amber" />
      <StatCard title="累计学分" :value="stats.credits" desc="已选课程对应学分总和" theme="violet" />
    </div>

    <section class="panel panel-inner" v-loading="loading">
      <template v-if="items.length">
        <el-table :data="items">
          <el-table-column prop="course_code" label="课程编号" min-width="110" />
          <el-table-column prop="course_name" label="课程名称" min-width="180" />
          <el-table-column prop="teacher_name" label="授课教师" min-width="110" />
          <el-table-column prop="term" label="学期" min-width="120" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span class="status-tag" :class="row.status === 'open' ? 'is-open' : 'is-closed'">
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="成绩" width="100">
            <template #default="{ row }">{{ row.score ?? '待录入' }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="warning" :disabled="row.score != null" @click="handleDrop(row)">退课</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <EmptyState v-else title="你还没有选课记录" />
    </section>
  </div>
</template>
