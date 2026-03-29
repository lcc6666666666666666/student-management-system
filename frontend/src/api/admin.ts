import request from './request'

import type {
  AdminCourseStatsOverview,
  AdminDepartmentStatsOverview,
  AdminProfile,
  AdminStudentCoursesResponse,
  AdminStudentItem,
  CourseFormOption,
  CourseItem,
  CourseScheduleItem,
  DepartmentItem,
  PageData
} from '@/types'

export function fetchAdminProfileApi() {
  return request.get<never, AdminProfile>('/admins/me/profile')
}

export function fetchAdminCoursesApi(params: Record<string, unknown>) {
  return request.get<never, PageData<CourseItem>>('/admins/courses', { params })
}

export function createCourseApi(payload: Record<string, unknown>) {
  return request.post('/admins/courses', payload)
}

export function updateCourseApi(courseId: number, payload: Record<string, unknown>) {
  return request.put(`/admins/courses/${courseId}`, payload)
}

export function deleteCourseApi(courseId: number) {
  return request.delete(`/admins/courses/${courseId}`)
}

export function fetchAdminCourseStatsApi() {
  return request.get<never, AdminCourseStatsOverview>('/admins/statistics/courses')
}

export function fetchAdminDepartmentsApi(params: Record<string, unknown>) {
  return request.get<never, PageData<DepartmentItem>>('/admins/departments', { params })
}

export function createDepartmentApi(payload: Record<string, unknown>) {
  return request.post('/admins/departments', payload)
}

export function updateDepartmentApi(departmentId: number, payload: Record<string, unknown>) {
  return request.put(`/admins/departments/${departmentId}`, payload)
}

export function deleteDepartmentApi(departmentId: number) {
  return request.delete(`/admins/departments/${departmentId}`)
}

export function fetchAdminDepartmentStatsApi() {
  return request.get<never, AdminDepartmentStatsOverview>('/admins/statistics/departments')
}

export function fetchCourseFormOptionsApi() {
  return request.get<
    never,
    { teachers: CourseFormOption[]; departments: CourseFormOption[]; status_options: Array<{ label: string; value: string }> }
  >('/admins/options/course-form')
}

export function fetchAdminCourseSchedulesApi(courseId: number) {
  return request.get<never, { course: { id: number; course_code: string; name: string; term: string }; items: CourseScheduleItem[] }>(
    `/admins/courses/${courseId}/schedules`
  )
}

export function createCourseScheduleApi(courseId: number, payload: Record<string, unknown>) {
  return request.post(`/admins/courses/${courseId}/schedules`, payload)
}

export function updateCourseScheduleApi(scheduleId: number, payload: Record<string, unknown>) {
  return request.put(`/admins/course-schedules/${scheduleId}`, payload)
}

export function deleteCourseScheduleApi(scheduleId: number) {
  return request.delete(`/admins/course-schedules/${scheduleId}`)
}

export function fetchAdminStudentsApi(params: Record<string, unknown>) {
  return request.get<never, PageData<AdminStudentItem>>('/admins/students', { params })
}

export function fetchAdminStudentCoursesApi(studentId: number) {
  return request.get<never, AdminStudentCoursesResponse>(`/admins/students/${studentId}/courses`)
}

export function assignStudentCourseApi(studentId: number, courseId: number) {
  return request.post(`/admins/students/${studentId}/courses/${courseId}`)
}

export function dropStudentCourseApi(studentId: number, courseId: number) {
  return request.delete(`/admins/students/${studentId}/courses/${courseId}`)
}
