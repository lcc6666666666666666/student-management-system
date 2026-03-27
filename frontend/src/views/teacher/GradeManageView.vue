<script setup lang="ts">
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchTeacherCourseStatsApi, fetchTeacherCourseStudentsApi, fetchTeacherCoursesApi, updateEnrollmentScoreApi } from '@/api/teacher'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { TeacherCourseItem, TeacherCourseStats, TeacherCourseStudentItem } from '@/types'

const route = useRoute()
const loading = ref(false)
const courseLoading = ref(false)
const courses = ref<TeacherCourseItem[]>([])
const selectedCourseId = ref<number | null>(null)
const students = ref<TeacherCourseStudentItem[]>([])
const stats = ref<TeacherCourseStats | null>(null)
const scoreMap = reactive<Record<number, number | null>>({})

const currentCourse = computed(() => courses.value.find((item) => item.id === selectedCourseId.value) || null)

async function loadCourses() {
  courseLoading.value = true
  try {
    const data = await fetchTeacherCoursesApi()
    courses.value = data.items
    const routeCourseId = Number(route.query.courseId || 0)
    selectedCourseId.value = courses.value.find((item) => item.id === routeCourseId)?.id || courses.value[0]?.id || null
  } finally {
    courseLoading.value = false
  }
}

async function loadCourseDetail(courseId: number) {
  loading.value = true
  try {
    const [studentData, statsData] = await Promise.all([
      fetchTeacherCourseStudentsApi(courseId),
      fetchTeacherCourseStatsApi(courseId)
    ])
    students.value = studentData.items
    stats.value = statsData
    studentData.items.forEach((item) => {
      scoreMap[item.enrollment_id] = item.score ?? null
    })
  } finally {
    loading.value = false
  }
}

async function saveScore(row: TeacherCourseStudentItem) {
  await updateEnrollmentScoreApi(row.enrollment_id, scoreMap[row.enrollment_id] ?? null)
  ElMessage.success(`已保存 ${row.student_name} 的成绩`)
  if (selectedCourseId.value) {
    await loadCourseDetail(selectedCourseId.value)
  }
}

watch(selectedCourseId, (value) => {
  if (value) {
    loadCourseDetail(value)
  }
})

onMounted(loadCourses)
</script>

<template>
  <div class="page-view">
    <PageHero
      title="成绩管理"
      description="教师可查看所授课程学生名单、录入成绩并实时查看统计分析结果。"
      tag="教师端"
    >
      <el-select v-model="selectedCourseId" placeholder="请选择课程" style="width: 240px" :loading="courseLoading">
        <el-option v-for="item in courses" :key="item.id" :label="`${item.course_code}｜${item.name}`" :value="item.id" />
      </el-select>
    </PageHero>

    <template v-if="selectedCourseId && stats">
      <div class="card-grid">
        <StatCard title="课程人数" :value="stats.selected_count" desc="当前课程选课总人数" theme="primary" />
        <StatCard title="平均成绩" :value="stats.avg_score ?? '--'" desc="课程当前平均成绩" theme="emerald" />
        <StatCard title="通过人数" :value="stats.pass_count" desc="成绩达到 60 分及以上" theme="amber" />
        <StatCard title="通过率" :value="stats.pass_rate ? `${stats.pass_rate}%` : '--'" desc="课程整体通过率" theme="violet" />
      </div>

      <section class="panel panel-inner" v-loading="loading">
        <div style="margin-bottom: 16px">
          <h3 class="section-title">{{ currentCourse?.name }}</h3>
          <p class="section-subtitle">
            {{ currentCourse?.course_code }} / {{ currentCourse?.term }} / 当前已选 {{ currentCourse?.selected_count }} 人
          </p>
        </div>

        <template v-if="students.length">
          <el-table :data="students">
            <el-table-column prop="student_no" label="学号" min-width="110" />
            <el-table-column prop="student_name" label="姓名" min-width="100" />
            <el-table-column prop="grade" label="年级" min-width="100" />
            <el-table-column prop="class_name" label="班级" min-width="120" />
            <el-table-column prop="department_name" label="院系" min-width="120" />
            <el-table-column label="成绩录入" min-width="180">
              <template #default="{ row }">
                <el-input-number
                  v-model="scoreMap[row.enrollment_id]"
                  :min="0"
                  :max="100"
                  :precision="0"
                  controls-position="right"
                  style="width: 130px"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="saveScore(row)">保存</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <EmptyState v-else title="当前课程暂无学生" description="课程尚未有人选课，统计数据会在选课后自动变化。" />
      </section>
    </template>

    <EmptyState v-else-if="!courseLoading" title="暂无可管理课程" description="请先在授课课程中确认教师账号已绑定课程。" />
  </div>
</template>
