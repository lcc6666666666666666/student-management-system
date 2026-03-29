<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchStudentCoursesApi, fetchStudentTimetableApi } from '@/api/student'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import StatCard from '@/components/StatCard.vue'
import type { TimetableEntry, TimetableResponse } from '@/types'

type TimetableCell =
  | { type: 'empty' }
  | { type: 'skip' }
  | { type: 'entry'; entry: TimetableEntry; rowspan: number }

const loading = ref(false)
const timetable = ref<TimetableResponse | null>(null)
const termOptions = ref<string[]>([])
const selectedTerm = ref('')

const sectionCount = computed(() => {
  const maxSection = Math.max(...(timetable.value?.items.map((item) => item.end_section) || [8]))
  return Math.max(maxSection, 8)
})

const gridRows = computed(() => {
  const items = timetable.value?.items || []
  const startMap = new Map<string, TimetableEntry>()
  const skipSet = new Set<string>()

  items.forEach((item) => {
    startMap.set(`${item.weekday}-${item.start_section}`, item)
    for (let section = item.start_section + 1; section <= item.end_section; section += 1) {
      skipSet.add(`${item.weekday}-${section}`)
    }
  })

  return Array.from({ length: sectionCount.value }, (_, index) => {
    const section = index + 1
    const cells: TimetableCell[] = []

    for (let weekday = 1; weekday <= 7; weekday += 1) {
      const key = `${weekday}-${section}`
      if (skipSet.has(key)) {
        cells.push({ type: 'skip' })
        continue
      }

      const entry = startMap.get(key)
      if (entry) {
        cells.push({ type: 'entry', entry, rowspan: entry.end_section - entry.start_section + 1 })
      } else {
        cells.push({ type: 'empty' })
      }
    }

    return { section, cells }
  })
})

const sortedItems = computed(() =>
  [...(timetable.value?.items || [])].sort((left, right) => {
    if (left.weekday !== right.weekday) return left.weekday - right.weekday
    if (left.start_section !== right.start_section) return left.start_section - right.start_section
    return left.course_name.localeCompare(right.course_name, 'zh-CN')
  })
)

async function loadTermOptions() {
  const data = await fetchStudentCoursesApi()
  termOptions.value = [...new Set(data.items.map((item) => item.term))].sort((left, right) => right.localeCompare(left))
}

async function loadTimetable(term?: string) {
  loading.value = true
  try {
    const params = term ? { term } : undefined
    timetable.value = await fetchStudentTimetableApi(params)
    if (!selectedTerm.value && timetable.value.term) {
      selectedTerm.value = timetable.value.term
    }
  } finally {
    loading.value = false
  }
}

async function handleTermChange() {
  await loadTimetable(selectedTerm.value || undefined)
}

onMounted(async () => {
  await Promise.all([loadTermOptions(), loadTimetable()])
})
</script>

<template>
  <div class="page-view">
    <PageHero
      title="我的课表"
      description="课表基于已选课程与课程时间安排生成。默认展示最新学期，并提供周表与明细双视图。"
      tag="学生端"
    >
      <el-select v-model="selectedTerm" placeholder="选择学期" clearable style="width: 220px" @change="handleTermChange">
        <el-option v-for="term in termOptions" :key="term" :label="term" :value="term" />
      </el-select>
    </PageHero>

    <div class="card-grid" v-if="timetable">
      <StatCard title="当前学期" :value="timetable.term || '--'" desc="默认自动选择最新学期" theme="primary" />
      <StatCard title="已选课程" :value="timetable.summary.total_courses" desc="当前学期的已选课程总数" theme="emerald" />
      <StatCard title="已排课课程" :value="timetable.summary.scheduled_courses" desc="已配置时间安排的课程数量" theme="amber" />
      <StatCard title="未排课课程" :value="timetable.summary.unscheduled_courses" desc="尚未配置时间安排的课程数量" theme="violet" />
    </div>

    <section class="panel panel-inner" v-loading="loading">
      <template v-if="timetable">
        <template v-if="timetable.items.length">
          <div class="timetable-scroll">
            <table class="timetable-table">
              <thead>
                <tr>
                  <th class="time-col">节次</th>
                  <th v-for="weekday in timetable.weekdays" :key="weekday.value">{{ weekday.label }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in gridRows" :key="row.section">
                  <th class="time-col">第 {{ row.section }} 节</th>
                  <template v-for="(cell, index) in row.cells" :key="`${row.section}-${index}`">
                    <td v-if="cell.type === 'empty'" class="timetable-cell"></td>
                    <td
                      v-else-if="cell.type === 'entry'"
                      class="timetable-cell timetable-cell--filled"
                      :rowspan="cell.rowspan"
                    >
                      <div class="timetable-course">{{ cell.entry.course_name }}</div>
                      <div class="timetable-meta">{{ cell.entry.teacher_name }}</div>
                      <div class="timetable-meta">{{ cell.entry.location }}</div>
                      <div class="timetable-meta">第 {{ cell.entry.start_week }}-{{ cell.entry.end_week }} 周</div>
                    </td>
                  </template>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
        <EmptyState
          v-else
          title="当前学期没有可渲染的时间块"
          description="可能该学期尚未选课，或者课程尚未配置时间安排。"
        />
      </template>
      <EmptyState v-else title="暂无课表数据" description="如果你尚未选课，课表会在选课后自动生成。" />
    </section>

    <section class="dual-grid" v-if="timetable">
      <section class="panel panel-inner">
        <h3 class="section-title">课表明细</h3>
        <p class="section-subtitle">便于按星期、节次、地点查看全部时间块</p>
        <div v-if="sortedItems.length" class="highlight-list" style="margin-top: 18px">
          <div v-for="item in sortedItems" :key="`${item.course_id}-${item.weekday}-${item.start_section}`" class="highlight-item">
            <div>
              <strong>{{ item.course_name }}</strong>
              <div class="section-subtitle">
                {{ item.weekday_label }} / 第 {{ item.start_section }}-{{ item.end_section }} 节 / 第 {{ item.start_week }}-{{ item.end_week }} 周
              </div>
            </div>
            <div style="text-align: right">
              <div>{{ item.location }}</div>
              <div class="section-subtitle">{{ item.teacher_name }}</div>
            </div>
          </div>
        </div>
        <EmptyState v-else title="暂无明细" description="当前学期尚无可展示的课表时间块。" />
      </section>

      <section class="panel panel-inner">
        <h3 class="section-title">未排课课程</h3>
        <p class="section-subtitle">这些课程允许存在，但因没有 schedule，不会显示在周课表中</p>
        <div v-if="timetable.unscheduled_courses.length" class="highlight-list" style="margin-top: 18px">
          <div v-for="course in timetable.unscheduled_courses" :key="course.course_id" class="highlight-item">
            <div>
              <strong>{{ course.course_name }}</strong>
              <div class="section-subtitle">{{ course.course_code }} / {{ course.term }}</div>
            </div>
            <div>{{ course.teacher_name }}</div>
          </div>
        </div>
        <EmptyState v-else title="全部课程已排课" description="当前学期所有已选课程都配置了时间安排。" />
      </section>
    </section>
  </div>
</template>

<style scoped>
.timetable-scroll {
  overflow-x: auto;
}

.timetable-table {
  width: 100%;
  min-width: 860px;
  border-collapse: separate;
  border-spacing: 0;
}

.timetable-table th,
.timetable-table td {
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.timetable-table th {
  padding: 12px;
  background: rgba(248, 250, 252, 0.92);
  font-weight: 700;
}

.time-col {
  width: 90px;
  min-width: 90px;
}

.timetable-cell {
  height: 92px;
  padding: 10px;
  vertical-align: top;
  background: rgba(255, 255, 255, 0.7);
}

.timetable-cell--filled {
  background: linear-gradient(180deg, rgba(234, 241, 255, 0.95), rgba(255, 255, 255, 0.92));
}

.timetable-course {
  font-weight: 700;
}

.timetable-meta {
  margin-top: 6px;
  color: var(--color-subtitle);
  font-size: 12px;
  line-height: 1.5;
}
</style>
