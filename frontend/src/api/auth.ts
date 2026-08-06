import http from './http'
import type { AuthUser, TokenPair } from '@/types/auth'

export function login(email: string, password: string) {
  return http.post<TokenPair>('/auth/login', { email, password }).then((res) => res.data)
}

export function fetchMe() {
  return http.get<AuthUser>('/auth/me').then((res) => res.data)
}
