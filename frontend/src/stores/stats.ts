import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as statsApi from '@/api/stats'
import type { DashboardStats } from '@/types/stats'

export const useStatsStore = defineStore('stats', () => {
  const data = ref<DashboardStats | null>(null)
  const isLoading = ref(false)

  async function fetch(): Promise<void> {
    isLoading.value = true
    try {
      data.value = await statsApi.fetchStats()
    } finally {
      isLoading.value = false
    }
  }

  return {
    data,
    isLoading,
    fetch,
  }
})
