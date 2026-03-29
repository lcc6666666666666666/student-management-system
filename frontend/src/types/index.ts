export type RoleType = 'student' | 'teacher' | 'admin'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface UserInfo {
  id: number
  username: string
  role: RoleType
  real_name: string
  phone?: string | null
  email?: string | null
  profile?: Record<string, unknown> | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

export interface DashboardCard {
  title: string
  value: number | string
  desc: string
  theme: 'primary' | 'emerald' | 'amber' | 'violet'
}

export interface DashboardHighlight {
  label: string
  value: number | string
  extra?: string
}

export interface DashboardOverview {
  role: RoleType
  cards: DashboardCard[]
  highlights: DashboardHighlight[]
  announcements: string[]
}

export interface CourseScheduleItem {
  id: number
  course_id: number
  weekday: number
  weekday_label: string
  start_section: number
  end_section: number
  start_week: number
  end_week: number
  location: string
  display_text: string
  created_at?: string
  updated_at?: string
}

export interface CourseItem {
  id: number
  course_code: string
  name: string
  credit: number
  hours: number
  capacity: number
  term: string
  status: 'open' | 'closed'
  description?: string | null
  teacher_id: number
  teacher_name: string
  department_id?: number | null
  department_name?: string | null
  selected_count: number
  available_seats: number
  is_selected: boolean
  schedule_count: number
  schedules?: CourseScheduleItem[]
  score_stats?: {
    student_count: number
    avg_score?: number | null
    max_score?: number | null
    min_score?: number | null
  }
}

export interface PageData<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

export interface StudentProfile {
  id: number
  user_id: number
  username: string
  real_name: string
  phone?: string | null
  email?: string | null
  student_no: string
  gender?: string | null
  grade?: string | null
  class_name?: string | null
  admission_year?: number | null
  department_id?: number | null
  department_name?: string | null
}

export interface TeacherProfile {
  id: number
  user_id: number
  username: string
  real_name: string
  phone?: string | null
  email?: string | null
  teacher_no: string
  title?: string | null
  office?: string | null
  department_id?: number | null
  department_name?: string | null
}

export interface AdminProfile {
  id: number
  user_id: number
  username: string
  real_name: string
  phone?: string | null
  email?: string | null
  admin_no: string
  level: string
}

export interface StudentCourseItem {
  enrollment_id: number
  course_id: number
  course_code: string
  course_name: string
  teacher_name: string
  department_name?: string | null
  term: string
  credit: number
  hours: number
  status: 'open' | 'closed'
  score?: number | null
  selected_at: string
}

export interface GradeSummary {
  graded_count: number
  passed_count: number
  failed_count: number
  avg_score?: number | null
}

export interface GradeItem {
  enrollment_id: number
  course_code: string
  course_name: string
  teacher_name: string
  term: string
  credit: number
  score?: number | null
  status: string
}

export interface TeacherCourseItem {
  id: number
  course_code: string
  name: string
  term: string
  credit: number
  hours: number
  capacity: number
  status: 'open' | 'closed'
  department_name?: string | null
  selected_count: number
  avg_score?: number | null
}

export interface TeacherCourseStudentItem {
  enrollment_id: number
  student_id: number
  student_no: string
  student_name: string
  grade?: string | null
  class_name?: string | null
  department_name?: string | null
  score?: number | null
  selected_at: string
}

export interface TeacherCourseStats {
  course_id: number
  course_name: string
  selected_count: number
  avg_score?: number | null
  max_score?: number | null
  min_score?: number | null
  pass_count: number
  fail_count: number
  pass_rate?: number | null
}

export interface AdminCourseStatsOverview {
  summary: {
    total_courses: number
    open_courses: number
    closed_courses: number
    total_enrollments: number
    average_capacity?: number | null
  }
  hot_courses: Array<{
    course_id: number
    course_code: string
    course_name: string
    term: string
    capacity: number
    selected_count: number
    occupancy_rate: number
  }>
}

export interface CourseFormOption {
  id: number
  name: string
  code?: string
  title?: string | null
  department_id?: number | null
  department_name?: string | null
  teacher_no?: string
}

export interface AdminStudentItem {
  id: number
  user_id: number
  student_no: string
  username: string
  real_name: string
  grade?: string | null
  class_name?: string | null
  department_name?: string | null
  selected_course_count: number
}

export interface AdminStudentSummary {
  id: number
  student_no: string
  real_name: string
  username: string
  grade?: string | null
  class_name?: string | null
  department_name?: string | null
}

export interface AdminStudentCoursesResponse {
  student: AdminStudentSummary
  total: number
  items: StudentCourseItem[]
}

export interface TimetableEntry {
  course_id: number
  course_code: string
  course_name: string
  teacher_name: string
  location: string
  weekday: number
  weekday_label: string
  start_section: number
  end_section: number
  start_week: number
  end_week: number
  term: string
}

export interface TimetableWeekday {
  value: number
  label: string
  items: TimetableEntry[]
}

export interface TimetableUnscheduledCourse {
  course_id: number
  course_code: string
  course_name: string
  teacher_name: string
  term: string
}

export interface TimetableResponse {
  term?: string | null
  summary: {
    total_courses: number
    scheduled_courses: number
    total_schedule_items: number
    unscheduled_courses: number
  }
  weekdays: TimetableWeekday[]
  items: TimetableEntry[]
  unscheduled_courses: TimetableUnscheduledCourse[]
}
