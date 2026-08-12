import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as newsApi from '@/api/news'
import type { NewsListParams } from '@/api/news'
import type { News } from '@/types/news'

export const useNewsStore = defineStore('news', () => {
  const items = ref<News[]>([])
  const isLoading = ref(false)

  async function fetchList(params: NewsListParams = {}): Promise<void> {
    isLoading.value = true
    try {
      items.value = await newsApi.fetchNews(params)
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    isLoading,
    fetchList,
  }
})
