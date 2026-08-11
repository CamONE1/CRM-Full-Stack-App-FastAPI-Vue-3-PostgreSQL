export type OfferStatus = 'draft' | 'sent' | 'accepted' | 'declined' | 'expired'

export interface Offer {
  id: number
  candidate_name: string
  candidate_email: string
  position: string
  salary_note: string | null
  status: OfferStatus
  created_by_id: number
  public_token: string | null
  expires_at: string | null
  responded_at: string | null
  is_archived: boolean
  archived_at: string | null
  created_at: string
}

export interface OfferListResponse {
  items: Offer[]
  total: number
}

export interface OfferCreate {
  candidate_name: string
  candidate_email: string
  position: string
  salary_note?: string
  expires_at?: string
}

export interface OfferUpdate {
  candidate_name?: string
  candidate_email?: string
  position?: string
  salary_note?: string
  expires_at?: string
}

// Candidate-facing view — deliberately excludes id/candidate_email/created_by_id/public_token.
export interface OfferPublic {
  candidate_name: string
  position: string
  salary_note: string | null
  status: OfferStatus
  expires_at: string | null
  responded_at: string | null
}

export type OfferRespondAction = 'accept' | 'decline'
