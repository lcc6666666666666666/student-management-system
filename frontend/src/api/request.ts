import axios from 'axios'
import { ElMessage } from 'element-plus'

import type { ApiResponse } from '@/types'
import { storage } from '@/utils/storage'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 12000
})

request.interceptors.request.use((config) => {
  const token = storage.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response): any => {
    const payload = response.data as ApiResponse<unknown>
    if (payload.code !== 0) {
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(new Error(payload.message || '请求失败'))
    }
    return payload.data
  },
  (error) => {
    const message = error?.response?.data?.message || error.message || '网络请求失败'
    if (error?.response?.status === 401) {
      storage.clearAll()
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
    }
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
