<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { fetchCourseDetailApi, fetchCourseListApi } from '@/api/courses'
import { dropCourseApi, enrollCourseApi } from '@/api/student'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { CourseItem, PageData } from '@/types'
import { getStatusLabel } from '@/utils/role'

const loading = ref(false)
const detailLoading = ref(false)
const detailVisible = ref(false)
const detail = ref<CourseItem | null>(null)

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

const stats = computed(() => {
  const items = pageData.value.items
  const openCount = items.filter((item) => item.status === 'open').length
  const selectedCount = items.filter((item) => item.is_selected).length
  const remainAvg = items.length ? Math.round(items.reduce((sum, item) => sum + item.available_seats, 0) / items.length) : 0
  return { openCount, selectedCount, remainAvg }
})

async function loadData() {
  loading.value = true
  try {
    pageData.value = await fetchCourseListApi(filters)
  } finally {
    loading.value = false
  }
}

async function openDetail(row: CourseItem) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await fetchCourseDetailApi(row.id)
  } finally {
    detailLoading.value = false
  }
}

async function handleEnroll(row: CourseItem) {
  await enrollCourseApi(row.id)
  ElMessage.success(`已选中《${row.name}》`)
  await loadData()
}

async function handleDrop(row: CourseItem) {
  await ElMessageBox.confirm(`确认退掉《${row.name}》吗？`, '退课确认', { type: 'warning' })
  await dropCourseApi(row.id)
  ElMessage.success('退课成功')
  await loadData()
}

function resetFilters() {
  filters.keyword = ''
  filters.status = ''
  filters.term = ''
  filters.page = 1
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-view">
    <PageHero
      title="课程列表"
      tag="学生端"
    >
      <el-button type="primary" @click="loadData">刷新列表</el-button>
    </PageHero>

    <div class="card-grid">
      <StatCard title="当前课程" :value="pageData.total" desc="筛选条件下的课程总数" theme="primary" />
      <StatCard title="开放课程" :value="stats.openCount" desc="当前页可选课程数量" theme="emerald" />
      <StatCard title="已选课程" :value="stats.selectedCount" desc="当前页中你已选中的课程数" theme="amber" />
      <StatCard title="平均余量" :value="stats.remainAvg" desc="当前页课程的平均剩余名额" theme="violet" />
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
          <el-table-column prop="term" label="学期" min-width="130" />
          <el-table-column prop="schedule_count" label="时间安排" width="100" />
          <el-table-column prop="credit" label="学分" width="80" />
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
                <el-button
                  v-if="!row.is_selected"
                  link
                  type="success"
                  :disabled="row.status !== 'open'"
                  @click="handleEnroll(row)"
                >
                  选课
                </el-button>
                <el-button v-else link type="warning" @click="handleDrop(row)">退课</el-button>
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
      <EmptyState v-else title="没有匹配课程" />
    </section>

    <el-drawer v-model="detailVisible" title="课程详情" size="520px">
      <div v-loading="detailLoading">
        <template v-if="detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="课程名称">{{ detail.name }}</el-descriptions-item>
            <el-descriptions-item label="课程编号">{{ detail.course_code }}</el-descriptions-item>
            <el-descriptions-item label="授课教师">{{ detail.teacher_name }}</el-descriptions-item>
            <el-descriptions-item label="所属院系">{{ detail.department_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="学期">{{ detail.term }}</el-descriptions-item>
            <el-descriptions-item label="课程状态">{{ getStatusLabel(detail.status) }}</el-descriptions-item>
            <el-descriptions-item label="课程描述">{{ detail.description || '暂无描述' }}</el-descriptions-item>
          </el-descriptions>

          <div class="card-grid" style="margin-top: 18px">
            <StatCard title="已选人数" :value="detail.score_stats?.student_count || detail.selected_count" desc="当前课程选课人数" theme="primary" />
            <StatCard title="平均成绩" :value="detail.score_stats?.avg_score ?? '--'" desc="若尚未录入成绩则显示为空" theme="amber" />
          </div>

          <section class="schedule-wrap">
            <div>
              <h3 class="section-title">上课时间安排</h3>
              <p class="section-subtitle">按星期、节次和周次展示课程安排</p>
            </div>
            <div v-if="detail.schedules?.length" class="highlight-list" style="margin-top: 16px">
              <div v-for="schedule in detail.schedules" :key="schedule.id" class="highlight-item">
                <div>
                  <strong>{{ schedule.weekday_label }}</strong>
                  <div class="section-subtitle">第 {{ schedule.start_section }}-{{ schedule.end_section }} 节 / 第 {{ schedule.start_week }}-{{ schedule.end_week }} 周</div>
                </div>
                <div>{{ schedule.location }}</div>
              </div>
            </div>
            <el-empty v-else />
          </section>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.schedule-wrap {
  margin-top: 22px;
}
</style>
