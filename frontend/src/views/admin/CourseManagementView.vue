<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createCourseApi,
  deleteCourseApi,
  fetchAdminCourseStatsApi,
  fetchAdminCoursesApi,
  fetchCourseFormOptionsApi,
  updateCourseApi
} from '@/api/admin'
import { fetchCourseDetailApi } from '@/api/courses'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { AdminCourseStatsOverview, CourseFormOption, CourseItem, PageData } from '@/types'
import { getStatusLabel } from '@/utils/role'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const drawerVisible = ref(false)
const detailLoading = ref(false)
const formRef = ref<FormInstance>()

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

const rules: FormRules<typeof form> = {
  course_code: [{ required: true, message: '请输入课程编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  teacher_id: [{ required: true, message: '请选择授课教师', trigger: 'change' }],
  credit: [{ required: true, message: '请输入课程学分', trigger: 'change' }],
  hours: [{ required: true, message: '请输入学时', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入课程容量', trigger: 'change' }]
}

const dialogTitle = computed(() => (form.id ? '编辑课程' : '新增课程'))

async function loadData() {
  loading.value = true
  try {
    const [listData, statsData] = await Promise.all([
      fetchAdminCoursesApi(filters),
      fetchAdminCourseStatsApi()
    ])
    pageData.value = listData
    stats.value = statsData
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  options.value = await fetchCourseFormOptionsApi()
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
  await ElMessageBox.confirm(`确认删除《${row.name}》吗？若已有选课记录将被后端拦截。`, '删除确认', { type: 'warning' })
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
      description="管理员可以进行课程信息增删改查，查看课程选课人数、容量占用率，并维护课程开放状态。"
      tag="管理员端"
    >
      <el-button type="primary" @click="openCreateDialog">新增课程</el-button>
    </PageHero>

    <div class="card-grid">
      <StatCard title="课程总数" :value="stats.summary.total_courses" desc="系统课程总量" theme="primary" />
      <StatCard title="开放课程" :value="stats.summary.open_courses" desc="当前允许学生选课的课程" theme="emerald" />
      <StatCard title="选课总数" :value="stats.summary.total_enrollments" desc="所有课程选课记录总量" theme="amber" />
      <StatCard title="平均容量" :value="stats.summary.average_capacity ?? '--'" desc="全部课程平均容量配置" theme="violet" />
    </div>

    <section class="panel panel-inner">
      <div class="toolbar">
        <div class="toolbar-filters">
          <el-input v-model="filters.keyword" placeholder="搜索课程名称或编号" clearable @keyup.enter="loadData" />
          <el-select v-model="filters.status" clearable placeholder="筛选状态">
            <el-option label="开放中" value="open" />
            <el-option label="已关闭" value="closed" />
          </el-select>
          <el-input v-model="filters.term" placeholder="输入学期，如 2025-2026-2" clearable />
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
          <el-table-column prop="term" label="学期" min-width="120" />
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
          <el-table-column label="操作" min-width="220" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link type="primary" @click="openDetail(row)">详情</el-button>
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
      <p class="section-subtitle">用于展示课程容量和选课人数统计结果</p>
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

    <el-drawer v-model="drawerVisible" title="课程详情" size="480px">
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
        </template>
      </div>
    </el-drawer>
  </div>
</template>
