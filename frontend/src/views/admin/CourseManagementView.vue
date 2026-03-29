<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createCourseApi,
  createCourseScheduleApi,
  deleteCourseApi,
  deleteCourseScheduleApi,
  fetchAdminCourseSchedulesApi,
  fetchAdminCourseStatsApi,
  fetchAdminCoursesApi,
  fetchCourseFormOptionsApi,
  updateCourseApi,
  updateCourseScheduleApi
} from '@/api/admin'
import { fetchCourseDetailApi } from '@/api/courses'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { AdminCourseStatsOverview, CourseFormOption, CourseItem, CourseScheduleItem, PageData } from '@/types'
import { getStatusLabel } from '@/utils/role'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const drawerVisible = ref(false)
const detailLoading = ref(false)
const formRef = ref<FormInstance>()

const scheduleDrawerVisible = ref(false)
const scheduleDialogVisible = ref(false)
const scheduleLoading = ref(false)
const scheduleSaving = ref(false)
const scheduleFormRef = ref<FormInstance>()
const scheduleCourseId = ref<number | null>(null)

const weekdayOptions = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
]

const filters = reactive({
  keyword: '',
  status: '',
  term: '',
  page: 1,
  page_size: 8
})

const pageData = ref<PageData<CourseItem>>({
  total: 0,
  page: 1,
  page_size: 8,
  items: []
})

const stats = ref<AdminCourseStatsOverview>({
  summary: {
    total_courses: 0,
    open_courses: 0,
    closed_courses: 0,
    total_enrollments: 0,
    average_capacity: 0
  },
  hot_courses: []
})

const options = ref<{
  teachers: CourseFormOption[]
  departments: CourseFormOption[]
  status_options: Array<{ label: string; value: string }>
}>({
  teachers: [],
  departments: [],
  status_options: []
})

const form = reactive({
  id: 0,
  course_code: '',
  name: '',
  credit: 3,
  hours: 32,
  capacity: 40,
  term: '2025-2026-2',
  status: 'open',
  description: '',
  teacher_id: undefined as number | undefined,
  department_id: undefined as number | undefined
})

const detail = ref<CourseItem | null>(null)

const scheduleData = ref<{
  course: { id: number; course_code: string; name: string; term: string } | null
  items: CourseScheduleItem[]
}>({
  course: null,
  items: []
})

const scheduleForm = reactive({
  id: 0,
  weekday: 1,
  start_section: 1,
  end_section: 2,
  start_week: 1,
  end_week: 16,
  location: ''
})

const rules: FormRules<typeof form> = {
  course_code: [{ required: true, message: '请输入课程编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  teacher_id: [{ required: true, message: '请选择授课教师', trigger: 'change' }],
  credit: [{ required: true, message: '请输入课程学分', trigger: 'change' }],
  hours: [{ required: true, message: '请输入学时', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入课程容量', trigger: 'change' }]
}

const scheduleRules: FormRules<typeof scheduleForm> = {
  weekday: [{ required: true, message: '请选择星期', trigger: 'change' }],
  start_section: [{ required: true, message: '请输入开始节次', trigger: 'change' }],
  end_section: [{ required: true, message: '请输入结束节次', trigger: 'change' }],
  start_week: [{ required: true, message: '请输入起始周', trigger: 'change' }],
  end_week: [{ required: true, message: '请输入结束周', trigger: 'change' }],
  location: [{ required: true, message: '请输入上课地点', trigger: 'blur' }]
}

const dialogTitle = computed(() => (form.id ? '编辑课程' : '新增课程'))
const scheduleDialogTitle = computed(() => (scheduleForm.id ? '编辑时间安排' : '新增时间安排'))

async function loadData() {
  loading.value = true
  try {
    const [listData, statsData] = await Promise.all([fetchAdminCoursesApi(filters), fetchAdminCourseStatsApi()])
    pageData.value = listData
    stats.value = statsData
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  options.value = await fetchCourseFormOptionsApi()
}

async function loadCourseSchedules(courseId: number) {
  scheduleLoading.value = true
  try {
    scheduleData.value = await fetchAdminCourseSchedulesApi(courseId)
    scheduleCourseId.value = courseId
  } finally {
    scheduleLoading.value = false
  }
}

async function refreshCourseDetailIfNeeded(courseId: number) {
  if (detail.value?.id === courseId) {
    detail.value = await fetchCourseDetailApi(courseId)
  }
}

function resetForm() {
  form.id = 0
  form.course_code = ''
  form.name = ''
  form.credit = 3
  form.hours = 32
  form.capacity = 40
  form.term = '2025-2026-2'
  form.status = 'open'
  form.description = ''
  form.teacher_id = undefined
  form.department_id = undefined
}

function resetScheduleForm() {
  scheduleForm.id = 0
  scheduleForm.weekday = 1
  scheduleForm.start_section = 1
  scheduleForm.end_section = 2
  scheduleForm.start_week = 1
  scheduleForm.end_week = 16
  scheduleForm.location = ''
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: CourseItem) {
  form.id = row.id
  form.course_code = row.course_code
  form.name = row.name
  form.credit = row.credit
  form.hours = row.hours
  form.capacity = row.capacity
  form.term = row.term
  form.status = row.status
  form.description = row.description || ''
  form.teacher_id = row.teacher_id
  form.department_id = row.department_id || undefined
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      course_code: form.course_code,
      name: form.name,
      credit: form.credit,
      hours: form.hours,
      capacity: form.capacity,
      term: form.term,
      status: form.status,
      description: form.description,
      teacher_id: form.teacher_id,
      department_id: form.department_id
    }
    if (form.id) {
      await updateCourseApi(form.id, payload)
      ElMessage.success('课程更新成功')
    } else {
      await createCourseApi(payload)
      ElMessage.success('课程创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: CourseItem) {
  await ElMessageBox.confirm(`确认删除《${row.name}》吗？若已有选课记录会被后端拦截。`, '删除确认', { type: 'warning' })
  await deleteCourseApi(row.id)
  ElMessage.success('课程删除成功')
  await loadData()
}

async function openDetail(row: CourseItem) {
  drawerVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await fetchCourseDetailApi(row.id)
  } finally {
    detailLoading.value = false
  }
}

async function openScheduleManager(row: CourseItem) {
  scheduleDrawerVisible.value = true
  await loadCourseSchedules(row.id)
}

function openCreateSchedule() {
  resetScheduleForm()
  scheduleDialogVisible.value = true
}

function openEditSchedule(item: CourseScheduleItem) {
  scheduleForm.id = item.id
  scheduleForm.weekday = item.weekday
  scheduleForm.start_section = item.start_section
  scheduleForm.end_section = item.end_section
  scheduleForm.start_week = item.start_week
  scheduleForm.end_week = item.end_week
  scheduleForm.location = item.location
  scheduleDialogVisible.value = true
}

async function submitSchedule() {
  if (!scheduleFormRef.value || !scheduleCourseId.value) return
  const valid = await scheduleFormRef.value.validate().catch(() => false)
  if (!valid) return

  scheduleSaving.value = true
  try {
    const payload = {
      weekday: scheduleForm.weekday,
      start_section: scheduleForm.start_section,
      end_section: scheduleForm.end_section,
      start_week: scheduleForm.start_week,
      end_week: scheduleForm.end_week,
      location: scheduleForm.location
    }
    if (scheduleForm.id) {
      await updateCourseScheduleApi(scheduleForm.id, payload)
      ElMessage.success('时间安排更新成功')
    } else {
      await createCourseScheduleApi(scheduleCourseId.value, payload)
      ElMessage.success('时间安排创建成功')
    }
    scheduleDialogVisible.value = false
    await Promise.all([loadCourseSchedules(scheduleCourseId.value), loadData(), refreshCourseDetailIfNeeded(scheduleCourseId.value)])
  } finally {
    scheduleSaving.value = false
  }
}

async function handleDeleteSchedule(item: CourseScheduleItem) {
  await ElMessageBox.confirm(`确认删除该时间安排吗？\n${item.display_text}`, '删除确认', { type: 'warning' })
  await deleteCourseScheduleApi(item.id)
  ElMessage.success('时间安排删除成功')
  if (scheduleCourseId.value) {
    await Promise.all([loadCourseSchedules(scheduleCourseId.value), loadData(), refreshCourseDetailIfNeeded(scheduleCourseId.value)])
  }
}

function resetFilters() {
  filters.keyword = ''
  filters.status = ''
  filters.term = ''
  filters.page = 1
  loadData()
}

onMounted(async () => {
  await Promise.all([loadOptions(), loadData()])
})
</script>

<template>
  <div class="page-view">
    <PageHero
      title="课程管理"
      description="管理员可以维护课程基础信息、查看选课统计，并直接维护每门课程的时间安排。"
      tag="管理员端"
    >
      <el-button type="primary" @click="openCreateDialog">新增课程</el-button>
    </PageHero>

    <div class="card-grid">
      <StatCard title="课程总数" :value="stats.summary.total_courses" desc="系统当前课程总量" theme="primary" />
      <StatCard title="开放课程" :value="stats.summary.open_courses" desc="允许学生选课的课程数量" theme="emerald" />
      <StatCard title="选课总数" :value="stats.summary.total_enrollments" desc="所有课程选课记录总量" theme="amber" />
      <StatCard title="平均容量" :value="stats.summary.average_capacity ?? '--'" desc="全体课程的平均容量配置" theme="violet" />
    </div>

    <section class="panel panel-inner">
      <div class="toolbar">
        <div class="toolbar-filters">
          <el-input v-model="filters.keyword" placeholder="搜索课程名称或编号" clearable @keyup.enter="loadData" />
          <el-select v-model="filters.status" clearable placeholder="筛选状态">
            <el-option label="开放中" value="open" />
            <el-option label="已关闭" value="closed" />
          </el-select>
          <el-input v-model="filters.term" placeholder="输入学期，例如 2025-2026-2" clearable />
        </div>
        <div class="table-actions">
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="primary" @click="loadData">查询</el-button>
        </div>
      </div>
    </section>

    <section class="panel panel-inner" v-loading="loading">
      <template v-if="pageData.items.length">
        <el-table :data="pageData.items">
          <el-table-column prop="course_code" label="课程编号" min-width="110" />
          <el-table-column prop="name" label="课程名称" min-width="180" />
          <el-table-column prop="teacher_name" label="授课教师" min-width="110" />
          <el-table-column prop="department_name" label="所属院系" min-width="120" />
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
          <el-table-column label="操作" min-width="280" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link type="primary" @click="openDetail(row)">详情</el-button>
                <el-button link type="success" @click="openScheduleManager(row)">时间安排</el-button>
                <el-button link type="warning" @click="openEditDialog(row)">编辑</el-button>
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="pageData.total"
          :page-sizes="[8, 12, 20]"
          layout="total, sizes, prev, pager, next"
          @change="loadData"
        />
      </template>
      <EmptyState v-else title="当前没有课程数据" description="可以点击右上角新增课程，或检查数据库初始化结果。" />
    </section>

    <section class="panel panel-inner">
      <h3 class="section-title">热门课程占用率</h3>
      <p class="section-subtitle">展示课程容量与选课人数的统计结果</p>
      <div class="highlight-list" style="margin-top: 18px">
        <div v-for="item in stats.hot_courses" :key="item.course_id" class="highlight-item">
          <div>
            <strong>{{ item.course_name }}</strong>
            <div class="section-subtitle">{{ item.course_code }} / {{ item.term }}</div>
          </div>
          <div style="text-align: right">
            <div style="font-size: 22px; font-weight: 800">{{ item.occupancy_rate }}%</div>
            <div class="section-subtitle">{{ item.selected_count }} / {{ item.capacity }}</div>
          </div>
        </div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="18">
          <el-col :xs="24" :md="12">
            <el-form-item label="课程编号" prop="course_code">
              <el-input v-model="form.course_code" placeholder="例如 DB101" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="课程名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入课程名称" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="学分" prop="credit">
              <el-input-number v-model="form.credit" :min="0.5" :step="0.5" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="学时" prop="hours">
              <el-input-number v-model="form.hours" :min="8" :max="200" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="课程容量" prop="capacity">
              <el-input-number v-model="form.capacity" :min="1" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="授课教师" prop="teacher_id">
              <el-select v-model="form.teacher_id" placeholder="请选择教师">
                <el-option
                  v-for="teacher in options.teachers"
                  :key="teacher.id"
                  :label="`${teacher.name}（${teacher.teacher_no}）`"
                  :value="teacher.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="所属院系">
              <el-select v-model="form.department_id" placeholder="请选择院系" clearable>
                <el-option
                  v-for="department in options.departments"
                  :key="department.id"
                  :label="department.name"
                  :value="department.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="学期">
              <el-input v-model="form.term" placeholder="例如 2025-2026-2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="课程状态">
              <el-segmented
                v-model="form.status"
                :options="options.status_options.map((item) => ({ label: item.label, value: item.value }))"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="课程描述">
              <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入课程简介或教学目标" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="drawerVisible" title="课程详情" size="520px">
      <div v-loading="detailLoading">
        <template v-if="detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="课程名称">{{ detail.name }}</el-descriptions-item>
            <el-descriptions-item label="课程编号">{{ detail.course_code }}</el-descriptions-item>
            <el-descriptions-item label="授课教师">{{ detail.teacher_name }}</el-descriptions-item>
            <el-descriptions-item label="所属院系">{{ detail.department_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学期">{{ detail.term }}</el-descriptions-item>
            <el-descriptions-item label="课程状态">{{ getStatusLabel(detail.status) }}</el-descriptions-item>
            <el-descriptions-item label="课程容量">{{ detail.capacity }}</el-descriptions-item>
            <el-descriptions-item label="已选人数">{{ detail.selected_count }}</el-descriptions-item>
            <el-descriptions-item label="课程描述">{{ detail.description || '暂无描述' }}</el-descriptions-item>
          </el-descriptions>

          <section class="schedule-section">
            <h3 class="section-title">时间安排</h3>
            <p class="section-subtitle">课程详情中同步展示当前有效的时间安排</p>
            <div v-if="detail.schedules?.length" class="highlight-list" style="margin-top: 16px">
              <div v-for="schedule in detail.schedules" :key="schedule.id" class="highlight-item">
                <div>
                  <strong>{{ schedule.weekday_label }}</strong>
                  <div class="section-subtitle">第 {{ schedule.start_section }}-{{ schedule.end_section }} 节 / 第 {{ schedule.start_week }}-{{ schedule.end_week }} 周</div>
                </div>
                <div>{{ schedule.location }}</div>
              </div>
            </div>
            <el-empty v-else description="该课程暂未配置时间安排" />
          </section>
        </template>
      </div>
    </el-drawer>

    <el-drawer v-model="scheduleDrawerVisible" title="课程时间安排管理" size="720px">
      <div class="schedule-toolbar">
        <div>
          <h3 class="section-title">{{ scheduleData.course?.name || '课程时间安排' }}</h3>
          <p class="section-subtitle">{{ scheduleData.course?.course_code }} / {{ scheduleData.course?.term }}</p>
        </div>
        <el-button type="primary" @click="openCreateSchedule">新增时间安排</el-button>
      </div>

      <section class="panel panel-inner" style="margin-top: 18px" v-loading="scheduleLoading">
        <template v-if="scheduleData.items.length">
          <el-table :data="scheduleData.items">
            <el-table-column prop="weekday_label" label="星期" width="90" />
            <el-table-column label="节次" width="130">
              <template #default="{ row }">第 {{ row.start_section }}-{{ row.end_section }} 节</template>
            </el-table-column>
            <el-table-column label="周次" width="140">
              <template #default="{ row }">第 {{ row.start_week }}-{{ row.end_week }} 周</template>
            </el-table-column>
            <el-table-column prop="location" label="地点" min-width="150" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-button link type="warning" @click="openEditSchedule(row)">编辑</el-button>
                  <el-button link type="danger" @click="handleDeleteSchedule(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <EmptyState v-else title="暂无时间安排" description="点击右上角新增时间安排后会立即生效。" />
      </section>
    </el-drawer>

    <el-dialog v-model="scheduleDialogVisible" :title="scheduleDialogTitle" width="560px" destroy-on-close>
      <el-form ref="scheduleFormRef" :model="scheduleForm" :rules="scheduleRules" label-position="top">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="星期" prop="weekday">
              <el-select v-model="scheduleForm.weekday" placeholder="请选择星期">
                <el-option v-for="item in weekdayOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="上课地点" prop="location">
              <el-input v-model="scheduleForm.location" placeholder="例如 博学楼 A101" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="开始节次" prop="start_section">
              <el-input-number v-model="scheduleForm.start_section" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="结束节次" prop="end_section">
              <el-input-number v-model="scheduleForm.end_section" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="起始周" prop="start_week">
              <el-input-number v-model="scheduleForm.start_week" :min="1" :max="30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item label="结束周" prop="end_week">
              <el-input-number v-model="scheduleForm.end_week" :min="1" :max="30" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="scheduleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="scheduleSaving" @click="submitSchedule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.schedule-section {
  margin-top: 22px;
}

.schedule-toolbar {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
}
</style>
