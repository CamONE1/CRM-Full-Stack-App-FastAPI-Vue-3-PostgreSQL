import type { Offer, OfferStatus } from './offer'
import type { News } from './news'

export interface OffersStats {
  total: number
  by_status: Record<OfferStatus, number>
}

export interface EmployeesStats {
  total: number
  active: number
  inactive: number
  by_department: Record<string, number>
}

export interface DashboardStats {
  offers: OffersStats
  employees: EmployeesStats
  recent_offers: Offer[]
  recent_news: News[]
}
