<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchTeacherCoursesApi } from '@/api/teacher'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { TeacherCourseItem } from '@/types'
import { getStatusLabel } from '@/utils/role'

const router = useRouter()
const loading = ref(false)
const items = ref<TeacherCourseItem[]>([])
const summary = ref({
  course_count: 0,
  student_count: 0,
  graded_course_count: 0
})

async function loadData() {
  loading.value = true
  try {
    const data = await fetchTeacherCoursesApi()
    items.value = data.items
    summary.value = data.summary
  } finally {
    loading.value = false
  }
}

function toGradePage(courseId: number) {
  router.push({ path: '/teacher/grades', query: { courseId: String(courseId) } })
}

onMounted(loadData)
</script>

<template>
  <div class="page-view">
    <PageHero
      title="授课课程"
      description="教师可查看本人授课课程、课程容量、选课人数和平均成绩，并快速进入成绩管理。"
      tag="教师端"
    >
      <el-button type="primary" @click="loadData">刷新课程</el-button>
    </PageHero>

    <div class="card-grid">
      <StatCard title="授课课程" :value="summary.course_count" desc="当前账号承担的课程总数" theme="primary" />
      <StatCard title="选课人数" :value="summary.student_count" desc="教师名下课程累计选课人数" theme="emerald" />
      <StatCard title="已评分课程" :value="summary.graded_course_count" desc="已形成平均成绩的课程数量" theme="amber" />
      <StatCard title="待管理课程" :value="summary.course_count - summary.graded_course_count" desc="仍需继续录入或维护成绩" theme="violet" />
    </div>

    <section class="panel panel-inner" v-loading="loading">
      <template v-if="items.length">
        <el-table :data="items">
          <el-table-column prop="course_code" label="课程编号" min-width="110" />
          <el-table-column prop="name" label="课程名称" min-width="180" />
          <el-table-column prop="term" label="学期" min-width="120" />
          <el-table-column prop="department_name" label="所属院系" min-width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span class="status-tag" :class="row.status === 'open' ? 'is-open' : 'is-closed'">
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="selected_count" label="选课人数" width="100" />
          <el-table-column label="平均成绩" width="100">
            <template #default="{ row }">{{ row.avg_score ?? '--' }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="160" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link type="primary" @click="toGradePage(row.id)">成绩管理</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <EmptyState v-else title="暂无授课课程" description="请确认教师账号是否已分配课程。" />
    </section>
  </div>
</template>
