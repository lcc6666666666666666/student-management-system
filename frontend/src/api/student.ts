import request from './request'

import type { GradeItem, GradeSummary, StudentCourseItem, StudentProfile, TimetableResponse } from '@/types'

export function fetchStudentProfileApi() {
  return request.get<never, StudentProfile>('/students/me/profile')
}

export function updateStudentProfileApi(payload: Partial<StudentProfile>) {
  return request.put<never, StudentProfile>('/students/me/profile', payload)
}

export function fetchStudentCoursesApi() {
  return request.get<never, { total: number; items: StudentCourseItem[] }>('/students/courses')
}

export function enrollCourseApi(courseId: number) {
  return request.post(`/students/courses/${courseId}/enroll`)
}

export function dropCourseApi(courseId: number) {
  return request.delete(`/students/courses/${courseId}/enroll`)
}

export function fetchStudentGradesApi() {
  return request.get<never, { summary: GradeSummary; items: GradeItem[] }>('/students/grades')
}

export function fetchStudentTimetableApi(params?: { term?: string }) {
  return request.get<never, TimetableResponse>('/students/timetable', { params })
}
