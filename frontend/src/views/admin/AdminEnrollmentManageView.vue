<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  assignStudentCourseApi,
  dropStudentCourseApi,
  fetchAdminCoursesApi,
  fetchAdminStudentCoursesApi,
  fetchAdminStudentsApi
} from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { AdminStudentCoursesResponse, AdminStudentItem, CourseItem, PageData } from '@/types'
import { getStatusLabel } from '@/utils/role'

const studentLoading = ref(false)
const courseLoading = ref(false)
const selectedCoursesLoading = ref(false)
const actionLoading = ref(false)

const studentFilters = reactive({
  keyword: '',
  page: 1,
  page_size: 8
})

const courseFilters = reactive({
  keyword: '',
  status: 'open',
  term: '',
  page: 1,
  page_size: 8
})

const studentPageData = ref<PageData<AdminStudentItem>>({
  total: 0,
  page: 1,
  page_size: 8,
  items: []
})

const coursePageData = ref<PageData<CourseItem>>({
  total: 0,
  page: 1,
  page_size: 8,
  items: []
})

const selectedStudentId = ref<number | null>(null)
const studentCourseData = ref<AdminStudentCoursesResponse | null>(null)

const selectedCourseIds = computed(() => new Set((studentCourseData.value?.items || []).map((item) => item.course_id)))
const selectedStudent = computed(() => studentPageData.value.items.find((item) => item.id === selectedStudentId.value) || null)
const stats = computed(() => ({
  studentCount: studentPageData.value.total,
  selectedCount: studentCourseData.value?.total || 0,
  availableCount: coursePageData.value.items.filter((item) => item.status === 'open').length,
  conflictHint: '代选课会自动复用容量、开放状态和时间冲突校验'
}))

async function loadStudents() {
  studentLoading.value = true
  try {
    const data = await fetchAdminStudentsApi(studentFilters)
    studentPageData.value = data
    if (!data.items.length) {
      selectedStudentId.value = null
      studentCourseData.value = null
      return
    }

    const exists = data.items.some((item) => item.id === selectedStudentId.value)
    if (!exists) {
      selectedStudentId.value = data.items[0].id
    }
    await loadSelectedStudentCourses()
  } finally {
    studentLoading.value = false
  }
}

async function loadCourses() {
  courseLoading.value = true
  try {
    coursePageData.value = await fetchAdminCoursesApi(courseFilters)
  } finally {
    courseLoading.value = false
  }
}

async function loadSelectedStudentCourses() {
  if (!selectedStudentId.value) {
    studentCourseData.value = null
    return
  }

  selectedCoursesLoading.value = true
  try {
    studentCourseData.value = await fetchAdminStudentCoursesApi(selectedStudentId.value)
  } finally {
    selectedCoursesLoading.value = false
  }
}

async function handleSelectStudent(student: AdminStudentItem) {
  if (selectedStudentId.value === student.id) return
  selectedStudentId.value = student.id
  await loadSelectedStudentCourses()
}

async function handleAssignCourse(course: CourseItem) {
  if (!selectedStudentId.value) return
  actionLoading.value = true
  try {
    await assignStudentCourseApi(selectedStudentId.value, course.id)
    ElMessage.success(`已为 ${studentCourseData.value?.student.real_name || '该学生'} 代选《${course.name}》`)
    await Promise.all([loadCourses(), loadStudents()])
  } finally {
    actionLoading.value = false
  }
}

async function handleDropCourse(courseId: number, courseName: string) {
  if (!selectedStudentId.value) return
  await ElMessageBox.confirm(`确认将《${courseName}》从该学生的已选课程中移除吗？`, '退课确认', { type: 'warning' })
  actionLoading.value = true
  try {
    await dropStudentCourseApi(selectedStudentId.value, courseId)
    ElMessage.success('退课成功')
    await Promise.all([loadCourses(), loadStudents()])
  } finally {
    actionLoading.value = false
  }
}

function resetStudentFilters() {
  studentFilters.keyword = ''
  studentFilters.page = 1
  loadStudents()
}

function resetCourseFilters() {
  courseFilters.keyword = ''
  courseFilters.status = 'open'
  courseFilters.term = ''
  courseFilters.page = 1
  loadCourses()
}

onMounted(async () => {
  await Promise.all([loadStudents(), loadCourses()])
})
</script>

<template>
  <div class="page-view">
    <PageHero
      title="代选课管理"
      tag="管理员端"
    />

    <div class="card-grid">
      <StatCard title="学生总数" :value="stats.studentCount" desc="当前筛选条件下的学生数量" theme="primary" />
      <StatCard title="已选课程" :value="stats.selectedCount" desc="当前选中学生的已选课程数" theme="emerald" />
      <StatCard title="开放课程" :value="stats.availableCount" desc="当前页可代选的开放课程数" theme="amber" />
      <StatCard title="校验说明" :value="'自动拦截'" :desc="stats.conflictHint" theme="violet" />
    </div>

    <section class="dual-grid">
      <section class="panel panel-inner" v-loading="studentLoading">
        <div class="toolbar">
          <div>
            <h3 class="section-title">学生列表</h3>
            <p class="section-subtitle">按学号、姓名或用户名搜索学生</p>
          </div>
        </div>

        <div class="toolbar" style="margin-top: 16px">
          <div class="toolbar-filters">
            <el-input v-model="studentFilters.keyword" placeholder="搜索学号 / 姓名 / 用户名" clearable @keyup.enter="loadStudents" />
          </div>
          <div class="table-actions">
            <el-button @click="resetStudentFilters">重置</el-button>
            <el-button type="primary" @click="loadStudents">查询</el-button>
          </div>
        </div>

        <div v-if="studentPageData.items.length" class="student-list">
          <button
            v-for="student in studentPageData.items"
            :key="student.id"
            class="student-card"
            :class="{ 'is-active': selectedStudentId === student.id }"
            @click="handleSelectStudent(student)"
          >
            <div class="student-card__header">
              <strong>{{ student.real_name }}</strong>
              <span>{{ student.student_no }}</span>
            </div>
            <div class="section-subtitle">
              {{ student.department_name || '未分配院系' }} / {{ student.grade || '未设置年级' }} / {{ student.class_name || '未设置班级' }}
            </div>
            <div class="student-card__meta">已选课程 {{ student.selected_course_count }} 门</div>
          </button>
        </div>
        <EmptyState v-else title="没有匹配学生" />

        <el-pagination
          v-model:current-page="studentFilters.page"
          v-model:page-size="studentFilters.page_size"
          :total="studentPageData.total"
          :page-sizes="[8, 12, 20]"
          layout="total, sizes, prev, pager, next"
          style="margin-top: 18px"
          @change="loadStudents"
        />
      </section>

      <section class="panel panel-inner" v-loading="selectedCoursesLoading || actionLoading">
        <template v-if="studentCourseData">
          <div class="toolbar">
            <div>
              <h3 class="section-title">{{ studentCourseData.student.real_name }}</h3>
              <p class="section-subtitle">
                {{ studentCourseData.student.student_no }} / {{ studentCourseData.student.department_name || '未分配院系' }} / {{ studentCourseData.student.grade || '未设置年级' }}
              </p>
            </div>
            <el-button @click="loadSelectedStudentCourses">刷新已选课程</el-button>
          </div>

          <div v-if="studentCourseData.items.length" class="highlight-list" style="margin-top: 18px">
            <div v-for="item in studentCourseData.items" :key="item.enrollment_id" class="highlight-item">
              <div>
                <strong>{{ item.course_name }}</strong>
                <div class="section-subtitle">{{ item.course_code }} / {{ item.teacher_name }} / {{ item.term }}</div>
              </div>
              <div class="table-actions">
                <span class="section-subtitle">{{ item.score ?? '未录成绩' }}</span>
                <el-button link type="danger" @click="handleDropCourse(item.course_id, item.course_name)">退课</el-button>
              </div>
            </div>
          </div>
          <EmptyState v-else title="该学生暂无已选课程" />
        </template>
        <EmptyState v-else title="请选择学生" />
      </section>
    </section>

    <section class="panel panel-inner" v-loading="courseLoading || actionLoading">
      <div class="toolbar">
        <div>
          <h3 class="section-title">可代选课程</h3>
          <p class="section-subtitle">管理员可为当前选中学生选择课程，重复选课和时间冲突会被后端拦截。</p>
        </div>
      </div>

      <div class="toolbar" style="margin-top: 16px">
        <div class="toolbar-filters">
          <el-input v-model="courseFilters.keyword" placeholder="搜索课程名称或编号" clearable @keyup.enter="loadCourses" />
          <el-select v-model="courseFilters.status" clearable placeholder="筛选状态">
            <el-option label="开放中" value="open" />
            <el-option label="已关闭" value="closed" />
          </el-select>
          <el-input v-model="courseFilters.term" placeholder="输入学期，例如 2025-2026-2" clearable />
        </div>
        <div class="table-actions">
          <el-button @click="resetCourseFilters">重置</el-button>
          <el-button type="primary" @click="loadCourses">查询</el-button>
        </div>
      </div>

      <template v-if="coursePageData.items.length">
        <el-table :data="coursePageData.items" style="margin-top: 18px">
          <el-table-column prop="course_code" label="课程编号" min-width="110" />
          <el-table-column prop="name" label="课程名称" min-width="180" />
          <el-table-column prop="teacher_name" label="授课教师" min-width="110" />
          <el-table-column prop="term" label="学期" min-width="130" />
          <el-table-column prop="schedule_count" label="时间安排" width="100" />
          <el-table-column label="容量/已选" width="120">
            <template #default="{ row }">{{ row.capacity }} / {{ row.selected_count }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span class="status-tag" :class="row.status === 'open' ? 'is-open' : 'is-closed'">
                {{ getStatusLabel(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                :disabled="!selectedStudentId || selectedCourseIds.has(row.id) || row.status !== 'open'"
                @click="handleAssignCourse(row)"
              >
                {{ selectedCourseIds.has(row.id) ? '已选' : '代选课' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="courseFilters.page"
          v-model:page-size="courseFilters.page_size"
          :total="coursePageData.total"
          :page-sizes="[8, 12, 20]"
          layout="total, sizes, prev, pager, next"
          style="margin-top: 18px"
          @change="loadCourses"
        />
      </template>
      <EmptyState v-else title="暂无可展示课程" />
    </section>
  </div>
</template>

<style scoped>
.student-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.student-card {
  width: 100%;
  padding: 16px 18px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.92);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.student-card.is-active {
  border-color: rgba(37, 99, 235, 0.28);
  background: rgba(234, 241, 255, 0.88);
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.08);
}

.student-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.student-card__meta {
  margin-top: 10px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
}
</style>
