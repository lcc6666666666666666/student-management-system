import request from './request'

import type { CourseItem, PageData } from '@/types'

export function fetchCourseListApi(params: Record<string, unknown>) {
  return request.get<never, PageData<CourseItem>>('/courses', { params })
}

export function fetchCourseDetailApi(courseId: number) {
  return request.get<never, CourseItem>(`/courses/${courseId}`)
}
