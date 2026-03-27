import type { RoleType } from '@/types'

export const roleLabelMap: Record<RoleType, string> = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

export function getHomePathByRole(role?: RoleType | null) {
  if (role === 'student') return '/student/courses'
  if (role === 'teacher') return '/teacher/courses'
  if (role === 'admin') return '/admin/courses'
  return '/dashboard'
}

export function getStatusLabel(status: 'open' | 'closed' | string) {
  return status === 'open' ? '开放中' : '已关闭'
}
