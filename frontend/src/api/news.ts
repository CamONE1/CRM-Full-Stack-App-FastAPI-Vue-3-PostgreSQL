import http from './http'
import type { News } from '@/types/news'

export interface NewsListParams {
  offset?: number
  limit?: number
}

export function fetchNews(params: NewsListParams = {}) {
  return http.get<News[]>('/news', { params }).then((res) => res.data)
}
