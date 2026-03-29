import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import AppLayout from '@/layout/AppLayout.vue'
import { pinia } from '@/store'
import { useAuthStore } from '@/store/auth'

const appChildren: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: { title: '仪表盘', roles: ['student', 'teacher', 'admin'], menu: true, icon: 'HomeFilled' }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/profile/ProfileView.vue'),
    meta: { title: '个人信息', roles: ['student', 'teacher', 'admin'], menu: true, icon: 'UserFilled' }
  },
  {
    path: '/student/courses',
    name: 'student-courses',
    component: () => import('@/views/student/CourseListView.vue'),
    meta: { title: '课程列表', roles: ['student'], menu: true, icon: 'Tickets' }
  },
  {
    path: '/student/my-courses',
    name: 'student-my-courses',
    component: () => import('@/views/student/MyCoursesView.vue'),
    meta: { title: '我的课程', roles: ['student'], menu: true, icon: 'Notebook' }
  },
  {
    path: '/student/timetable',
    name: 'student-timetable',
    component: () => import('@/views/student/TimetableView.vue'),
    meta: { title: '我的课表', roles: ['student'], menu: true, icon: 'Calendar' }
  },
  {
    path: '/student/grades',
    name: 'student-grades',
    component: () => import('@/views/student/MyGradesView.vue'),
    meta: { title: '我的成绩', roles: ['student'], menu: true, icon: 'DataLine' }
  },
  {
    path: '/teacher/courses',
    name: 'teacher-courses',
    component: () => import('@/views/teacher/TeachingCoursesView.vue'),
    meta: { title: '授课课程', roles: ['teacher'], menu: true, icon: 'Reading' }
  },
  {
    path: '/teacher/grades',
    name: 'teacher-grades',
    component: () => import('@/views/teacher/GradeManageView.vue'),
    meta: { title: '成绩管理', roles: ['teacher'], menu: true, icon: 'EditPen' }
  },
  {
    path: '/admin/courses',
    name: 'admin-courses',
    component: () => import('@/views/admin/CourseManagementView.vue'),
    meta: { title: '课程管理', roles: ['admin'], menu: true, icon: 'Management' }
  },
  {
    path: '/admin/departments',
    name: 'admin-departments',
    component: () => import('@/views/admin/DepartmentManagementView.vue'),
    meta: { title: '院系管理', roles: ['admin'], menu: true, icon: 'OfficeBuilding' }
  },
  {
    path: '/admin/enrollments',
    name: 'admin-enrollments',
    component: () => import('@/views/admin/AdminEnrollmentManageView.vue'),
    meta: { title: '代选课管理', roles: ['admin'], menu: true, icon: 'User' }
  }
]

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: appChildren
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

export function getMenuRoutes(role?: string | null) {
  return appChildren.filter((route) => route.meta?.menu && route.meta.roles?.includes(role as never))
}

router.beforeEach(async (to, _, next) => {
  const authStore = useAuthStore(pinia)

  if (to.meta.public) {
    if (to.path === '/login' && authStore.isLoggedIn) {
      next(authStore.homePath)
      return
    }
    next()
    return
  }

  if (!authStore.token) {
    next('/login')
    return
  }

  if (!authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch {
      authStore.logout()
      next('/login')
      return
    }
  }

  if (to.meta.roles && authStore.role && !to.meta.roles.includes(authStore.role)) {
    next(authStore.homePath)
    return
  }

  next()
})
