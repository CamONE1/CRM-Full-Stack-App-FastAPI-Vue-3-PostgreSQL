import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@/api/auth'
import { clearTokens, getAccessToken, setTokens } from '@/api/tokenStorage'
import type { AuthUser } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  // Flips to true once the initial session-restore attempt (on app boot) has finished.
  const isReady = ref(false)

  const isAuthenticated = computed(() => user.value !== null)
  const role = computed(() => user.value?.role ?? null)

  async function login(email: string, password: string): Promise<void> {
    const tokens = await authApi.login(email, password)
    setTokens(tokens.access_token, tokens.refresh_token)
    user.value = await authApi.fetchMe()
  }

  function logout(): void {
    clearTokens()
    user.value = null
  }

  async function restoreSession(): Promise<void> {
    if (getAccessToken()) {
      try {
        user.value = await authApi.fetchMe()
      } catch {
        clearTokens()
        user.value = null
      }
    }
    isReady.value = true
  }

  return { user, isReady, isAuthenticated, role, login, logout, restoreSession }
})
