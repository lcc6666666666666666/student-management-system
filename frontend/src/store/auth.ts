import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { fetchCurrentUserApi, loginApi } from '@/api/auth'
import type { LoginResponse, UserInfo } from '@/types'
import { getHomePathByRole } from '@/utils/role'
import { storage } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(storage.getToken())
  const user = ref<UserInfo | null>(storage.getUser<UserInfo>())

  const isLoggedIn = computed(() => Boolean(token.value))
  const role = computed(() => user.value?.role || null)
  const homePath = computed(() => getHomePathByRole(role.value))

  function setSession(data: LoginResponse) {
    token.value = data.access_token
    user.value = data.user
    storage.setToken(data.access_token)
    storage.setUser(data.user)
  }

  async function login(payload: { username: string; password: string }) {
    const data = await loginApi(payload)
    setSession(data)
    return data
  }

  async function fetchCurrentUser() {
    if (!token.value) return null
    const currentUser = await fetchCurrentUserApi()
    user.value = currentUser
    storage.setUser(currentUser)
    return currentUser
  }

  function logout() {
    token.value = null
    user.value = null
    storage.clearAll()
  }

  return { token, user, role, homePath, isLoggedIn, login, fetchCurrentUser, logout }
})
