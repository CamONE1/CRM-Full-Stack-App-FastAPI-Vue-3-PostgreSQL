import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from './tokenStorage'
import type { TokenPair } from '@/types/auth'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

http.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// Backend expects refresh_token as a query param (not JSON body) — see auth/router.py
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null

  const { data } = await axios.post<TokenPair>(
    `${import.meta.env.VITE_API_URL}/auth/refresh`,
    null,
    { params: { refresh_token: refreshToken } },
  )
  setTokens(data.access_token, data.refresh_token)
  return data.access_token
}

// Queues requests that hit a 401 while a refresh is already in flight,
// so a burst of concurrent 401s triggers only one /auth/refresh call.
let isRefreshing = false
let pendingRequests: Array<(token: string | null) => void> = []

function resolvePending(token: string | null): void {
  pendingRequests.forEach((resolve) => resolve(token))
  pendingRequests = []
}

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined
    const isAuthEndpoint = originalRequest?.url?.includes('/auth/login') ||
      originalRequest?.url?.includes('/auth/refresh')

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry || isAuthEndpoint) {
      throw error
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push((token) => {
          if (!token) {
            reject(error)
            return
          }
          originalRequest._retry = true
          originalRequest.headers.set('Authorization', `Bearer ${token}`)
          resolve(http(originalRequest))
        })
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const newToken = await refreshAccessToken()
      resolvePending(newToken)
      if (!newToken) throw error
      originalRequest.headers.set('Authorization', `Bearer ${newToken}`)
      return http(originalRequest)
    } catch (refreshError) {
      resolvePending(null)
      clearTokens()
      window.location.href = '/login'
      throw refreshError
    } finally {
      isRefreshing = false
    }
  },
)

export default http
