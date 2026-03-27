import request from './request'

import type { TeacherCourseItem, TeacherCourseStats, TeacherCourseStudentItem, TeacherProfile } from '@/types'

export function fetchTeacherProfileApi() {
  return request.get<never, TeacherProfile>('/teachers/me/profile')
}

export function updateTeacherProfileApi(payload: Partial<TeacherProfile>) {
  return request.put<never, TeacherProfile>('/teachers/me/profile', payload)
}

export function fetchTeacherCoursesApi() {
  return request.get<never, { summary: { course_count: number; student_count: number; graded_course_count: number }; items: TeacherCourseItem[] }>('/teachers/courses')
}

export function fetchTeacherCourseStudentsApi(courseId: number) {
  return request.get<never, { course: { id: number; course_code: string; name: string; term: string; capacity: number }; items: TeacherCourseStudentItem[] }>(`/teachers/courses/${courseId}/students`)
}

export function fetchTeacherCourseStatsApi(courseId: number) {
  return request.get<never, TeacherCourseStats>(`/teachers/courses/${courseId}/stats`)
}

export function updateEnrollmentScoreApi(enrollmentId: number, score: number | null) {
  return request.put(`/teachers/enrollments/${enrollmentId}/score`, { score })
}
