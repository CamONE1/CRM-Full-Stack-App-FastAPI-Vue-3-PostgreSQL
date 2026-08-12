import http from './http'
import type { DashboardStats } from '@/types/stats'

export function fetchStats() {
  return http.get<DashboardStats>('/stats').then((res) => res.data)
}
