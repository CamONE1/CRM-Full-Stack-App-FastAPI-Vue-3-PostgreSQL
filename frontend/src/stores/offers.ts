import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as offersApi from '@/api/offers'
import type { OfferListParams } from '@/api/offers'
import type { Offer, OfferCreate, OfferPublic, OfferRespondAction, OfferUpdate } from '@/types/offer'

export const useOffersStore = defineStore('offers', () => {
  const items = ref<Offer[]>([])
  const total = ref(0)
  const positions = ref<string[]>([])
  const current = ref<Offer | null>(null)
  const publicOffer = ref<OfferPublic | null>(null)
  const isLoading = ref(false)

  async function fetchList(params: OfferListParams): Promise<void> {
    isLoading.value = true
    try {
      const data = await offersApi.fetchOffers(params)
      items.value = data.items
      total.value = data.total
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPositions(): Promise<void> {
    positions.value = await offersApi.fetchPositions()
  }

  async function fetchById(id: number): Promise<void> {
    current.value = await offersApi.fetchOffer(id)
  }

  async function create(data: OfferCreate): Promise<Offer> {
    current.value = await offersApi.createOffer(data)
    return current.value
  }

  async function update(id: number, data: OfferUpdate): Promise<Offer> {
    current.value = await offersApi.updateOffer(id, data)
    return current.value
  }

  async function send(id: number): Promise<Offer> {
    current.value = await offersApi.sendOffer(id)
    return current.value
  }

  async function archive(id: number): Promise<void> {
    await offersApi.archiveOffer(id)
  }

  async function fetchPublic(token: string): Promise<void> {
    publicOffer.value = await offersApi.fetchPublicOffer(token)
  }

  async function respondPublic(token: string, action: OfferRespondAction): Promise<void> {
    publicOffer.value = await offersApi.respondToPublicOffer(token, action)
  }

  return {
    items,
    total,
    positions,
    current,
    publicOffer,
    isLoading,
    fetchList,
    fetchPositions,
    fetchById,
    create,
    update,
    send,
    archive,
    fetchPublic,
    respondPublic,
  }
})
