import type { OfferStatus } from '@/types/offer'

export const OFFER_STATUS_LABELS: Record<OfferStatus, string> = {
  draft: 'Черновик',
  sent: 'Отправлен',
  accepted: 'Принят',
  declined: 'Отклонён',
  expired: 'Истёк',
}

export const OFFER_STATUS_VARIANTS: Record<OfferStatus, 'green' | 'red' | 'gray' | 'blue' | 'orange'> = {
  draft: 'gray',
  sent: 'blue',
  accepted: 'green',
  declined: 'red',
  expired: 'orange',
}
