import http from './http'
import type {
  Offer,
  OfferCreate,
  OfferListResponse,
  OfferPublic,
  OfferRespondAction,
  OfferStatus,
  OfferUpdate,
} from '@/types/offer'

export interface OfferListParams {
  search?: string
  status?: OfferStatus
  position?: string
  include_archived?: boolean
  offset?: number
  limit?: number
}

export function fetchOffers(params: OfferListParams) {
  return http.get<OfferListResponse>('/offers', { params }).then((res) => res.data)
}

export function fetchPositions() {
  return http.get<string[]>('/offers/positions').then((res) => res.data)
}

export function fetchOffer(id: number) {
  return http.get<Offer>(`/offers/${id}`).then((res) => res.data)
}

export function createOffer(data: OfferCreate) {
  return http.post<Offer>('/offers', data).then((res) => res.data)
}

export function updateOffer(id: number, data: OfferUpdate) {
  return http.patch<Offer>(`/offers/${id}`, data).then((res) => res.data)
}

export function sendOffer(id: number) {
  return http.post<Offer>(`/offers/${id}/send`).then((res) => res.data)
}

export function archiveOffer(id: number) {
  return http.post<Offer>(`/offers/${id}/archive`).then((res) => res.data)
}

export function fetchPublicOffer(token: string) {
  return http.get<OfferPublic>(`/public/offers/${token}`).then((res) => res.data)
}

export function respondToPublicOffer(token: string, action: OfferRespondAction) {
  return http.post<OfferPublic>(`/public/offers/${token}/respond`, { action }).then((res) => res.data)
}
