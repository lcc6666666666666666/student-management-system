import request from './request'

import type { LoginResponse, UserInfo } from '@/types'

export function loginApi(payload: { username: string; password: string }) {
  return request.post<never, LoginResponse>('/auth/login', payload)
}

export function fetchCurrentUserApi() {
  return request.get<never, UserInfo>('/auth/me')
}
