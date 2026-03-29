<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

import {
  createDepartmentApi,
  deleteDepartmentApi,
  fetchAdminDepartmentsApi,
  fetchAdminDepartmentStatsApi,
  updateDepartmentApi
} from '@/api/admin'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { AdminDepartmentStatsOverview, DepartmentItem, PageData } from '@/types'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()

const filters = reactive({
  keyword: '',
  page: 1,
  page_size: 8
})

const pageData = ref<PageData<DepartmentItem>>({
  total: 0,
  page: 1,
  page_size: 8,
  items: []
})

const stats = ref<AdminDepartmentStatsOverview>({
  summary: {
    total_departments: 0,
    assigned_students: 0,
    assigned_teachers: 0,
    assigned_courses: 0
  },
  hot_departments: []
})

const form = reactive({
  id: 0,
  name: '',
  code: '',
  description: ''
})

const rules: FormRules<typeof form> = {
  name: [{ required: true, message: '请输入院系名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入院系编码', trigger: 'blur' }]
}

const dialogTitle = ref('新增院系')

function formatDate(value?: string | null) {
  if (!value) return '--'
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date(value))
}

async function loadData() {
  loading.value = true
  try {
    const [listData, statsData] = await Promise.all([fetchAdminDepartmentsApi(filters), fetchAdminDepartmentStatsApi()])
    pageData.value = listData
    stats.value = statsData
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.id = 0
  form.name = ''
  form.code = ''
  form.description = ''
}

function openCreateDialog() {
  resetForm()
  dialogTitle.value = '新增院系'
  dialogVisible.value = true
}

function openEditDialog(row: DepartmentItem) {
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.description = row.description || ''
  dialogTitle.value = '编辑院系'
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      name: form.name,
      code: form.code,
      description: form.description || null
    }
    if (form.id) {
      await updateDepartmentApi(form.id, payload)
      ElMessage.success('院系更新成功')
    } else {
      await createDepartmentApi(payload)
      ElMessage.success('院系创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: DepartmentItem) {
  await ElMessageBox.confirm(`确认删除“${row.name}”吗？若已关联学生、教师或课程，后端会拦截。`, '删除确认', {
    type: 'warning'
  })
  const nextPage = pageData.value.items.length === 1 && filters.page > 1 ? filters.page - 1 : filters.page
  await deleteDepartmentApi(row.id)
  filters.page = nextPage
  ElMessage.success('院系删除成功')
  await loadData()
}

function resetFilters() {
  filters.keyword = ''
  filters.page = 1
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-view">
    <PageHero title="院系管理" tag="管理员端">
      <el-button type="primary" @click="openCreateDialog">新增院系</el-button>
    </PageHero>

    <div class="card-grid">
      <StatCard title="院系总数" :value="stats.summary.total_departments" desc="当前系统中的院系数量" theme="primary" />
      <StatCard title="关联学生" :value="stats.summary.assigned_students" desc="已分配到院系的学生数量" theme="emerald" />
      <StatCard title="关联教师" :value="stats.summary.assigned_teachers" desc="已分配到院系的教师数量" theme="amber" />
      <StatCard title="关联课程" :value="stats.summary.assigned_courses" desc="已归属到院系的课程数量" theme="violet" />
    </div>

    <section class="panel panel-inner">
      <div class="toolbar">
        <div class="toolbar-filters">
          <el-input v-model="filters.keyword" placeholder="搜索院系名称或编码" clearable @keyup.enter="loadData" />
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
          <el-table-column prop="name" label="院系名称" min-width="160" />
          <el-table-column prop="code" label="院系编码" min-width="130" />
          <el-table-column label="简介" min-width="220">
            <template #default="{ row }">{{ row.description || '--' }}</template>
          </el-table-column>
          <el-table-column prop="student_count" label="学生数" width="90" />
          <el-table-column prop="teacher_count" label="教师数" width="90" />
          <el-table-column prop="course_count" label="课程数" width="90" />
          <el-table-column label="创建时间" min-width="130">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="160" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
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
      <EmptyState v-else title="暂无院系数据" />
    </section>

    <section class="panel panel-inner">
      <h3 class="section-title">院系关联概览</h3>
      <p class="section-subtitle">按学生、教师和课程的关联总量展示活跃院系</p>
      <div v-if="stats.hot_departments.length" class="highlight-list" style="margin-top: 18px">
        <div v-for="item in stats.hot_departments" :key="item.department_id" class="highlight-item">
          <div>
            <strong>{{ item.name }}</strong>
            <div class="section-subtitle">{{ item.code }}</div>
          </div>
          <div style="text-align: right">
            <div>学生 {{ item.student_count }} / 教师 {{ item.teacher_count }} / 课程 {{ item.course_count }}</div>
            <div class="section-subtitle">总关联 {{ item.total_related }}</div>
          </div>
        </div>
      </div>
      <EmptyState v-else title="暂无统计数据" />
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="院系名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入院系名称" />
        </el-form-item>
        <el-form-item label="院系编码" prop="code">
          <el-input v-model="form.code" placeholder="例如 CS / MATH" />
        </el-form-item>
        <el-form-item label="院系简介">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="可选" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
