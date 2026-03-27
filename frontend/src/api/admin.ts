import request from './request'

import type { AdminCourseStatsOverview, AdminProfile, CourseFormOption, CourseItem, PageData } from '@/types'

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

export function fetchCourseFormOptionsApi() {
  return request.get<never, { teachers: CourseFormOption[]; departments: CourseFormOption[]; status_options: Array<{ label: string; value: string }> }>('/admins/options/course-form')
}
