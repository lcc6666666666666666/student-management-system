import request from './request'

import type { DashboardOverview } from '@/types'

export function fetchDashboardOverviewApi() {
  return request.get<never, DashboardOverview>('/dashboard/overview')
}
