<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchStudentGradesApi } from '@/api/student'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { GradeItem, GradeSummary } from '@/types'

const loading = ref(false)
const items = ref<GradeItem[]>([])
const summary = ref<GradeSummary>({
  graded_count: 0,
  passed_count: 0,
  failed_count: 0,
  avg_score: null
})

async function loadData() {
  loading.value = true
  try {
    const data = await fetchStudentGradesApi()
    items.value = data.items
    summary.value = data.summary
  } finally {
    loading.value = false
  }
}

function scoreType(score?: number | null) {
  if (score == null) return 'info'
  if (score >= 90) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

onMounted(loadData)
</script>

<template>
  <div class="page-view">
    <PageHero
      title="我的成绩"
      tag="学生端"
    />

    <div class="card-grid">
      <StatCard title="已录成绩" :value="summary.graded_count" desc="已完成评分的课程数量" theme="primary" />
      <StatCard title="通过课程" :value="summary.passed_count" desc="成绩达到 60 分及以上" theme="emerald" />
      <StatCard title="未通过课程" :value="summary.failed_count" desc="低于 60 分的课程数量" theme="amber" />
      <StatCard title="平均成绩" :value="summary.avg_score ?? '--'" desc="已录入成绩课程平均分" theme="violet" />
    </div>

    <section class="panel panel-inner" v-loading="loading">
      <template v-if="items.length">
        <el-table :data="items">
          <el-table-column prop="course_code" label="课程编号" min-width="110" />
          <el-table-column prop="course_name" label="课程名称" min-width="180" />
          <el-table-column prop="teacher_name" label="授课教师" min-width="110" />
          <el-table-column prop="term" label="学期" min-width="120" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column label="成绩" width="110">
            <template #default="{ row }">
              <el-tag :type="scoreType(row.score)" effect="light" round>{{ row.score ?? '待录入' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110" />
        </el-table>
      </template>
      <EmptyState v-else title="暂无成绩数据" />
    </section>
  </div>
</template>
