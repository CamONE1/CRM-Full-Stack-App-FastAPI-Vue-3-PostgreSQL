<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useOffersStore } from '@/stores/offers'
import BaseButton from '@/components/base/BaseButton.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import { OFFER_STATUS_LABELS, OFFER_STATUS_VARIANTS } from '@/utils/offerStatus'

const route = useRoute()
const store = useOffersStore()

const token = route.params.token as string

const isLoading = ref(true)
const notFound = ref(false)
const isResponding = ref(false)
const actionError = ref('')

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

async function loadOffer(): Promise<void> {
  isLoading.value = true
  notFound.value = false
  store.clearPublic()
  try {
    await store.fetchPublic(token)
  } catch (error) {
    // Any failure (404 unknown token, 422 malformed token, network error) means
    // there's nothing valid to show a candidate — never leak internals to a
    // public, unauthenticated page.
    notFound.value = true
    if (!(axios.isAxiosError(error) && error.response?.status === 404)) {
      console.error('Failed to load public offer', error)
    }
  } finally {
    isLoading.value = false
  }
}

async function respond(action: 'accept' | 'decline'): Promise<void> {
  actionError.value = ''
  isResponding.value = true
  try {
    await store.respondPublic(token, action)
  } catch (error) {
    if (axios.isAxiosError(error) && typeof error.response?.data?.detail === 'string') {
      actionError.value = error.response.data.detail
    } else {
      actionError.value = 'Не удалось отправить ответ. Попробуйте обновить страницу.'
    }
    // The offer may have changed underneath us (e.g. expired between page load
    // and the click) — re-fetch so the UI reflects the real current status.
    await loadOffer()
  } finally {
    isResponding.value = false
  }
}

onMounted(loadOffer)
</script>

<template>
  <div class="w-full max-w-lg rounded-lg bg-white p-8 shadow">
    <p v-if="isLoading" class="text-sm text-gray-500">Загрузка…</p>

    <p v-else-if="notFound" class="text-sm text-gray-600">
      Оффер не найден. Проверьте, что ссылка скопирована полностью.
    </p>

    <template v-else-if="store.publicOffer">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-gray-400">HR-портал</p>
          <h1 class="mt-1 text-xl font-semibold text-gray-900">{{ store.publicOffer.position }}</h1>
        </div>
        <StatusBadge :variant="OFFER_STATUS_VARIANTS[store.publicOffer.status]">
          {{ OFFER_STATUS_LABELS[store.publicOffer.status] }}
        </StatusBadge>
      </div>

      <p class="mt-4 text-sm text-gray-700">Здравствуйте, {{ store.publicOffer.candidate_name }}!</p>
      <p v-if="store.publicOffer.salary_note" class="mt-3 text-sm text-gray-700">
        {{ store.publicOffer.salary_note }}
      </p>

      <div v-if="store.publicOffer.status === 'sent'" class="mt-6 space-y-4">
        <p class="text-xs text-gray-400">Оффер действителен до {{ formatDate(store.publicOffer.expires_at) }}</p>
        <p v-if="actionError" class="text-sm text-red-600">{{ actionError }}</p>
        <div class="flex items-center gap-3">
          <BaseButton :loading="isResponding" @click="respond('accept')">Принять</BaseButton>
          <BaseButton variant="secondary" :loading="isResponding" @click="respond('decline')">Отклонить</BaseButton>
        </div>
      </div>

      <p v-else-if="store.publicOffer.status === 'accepted'" class="mt-6 text-sm text-green-600">
        Вы приняли этот оффер. Мы свяжемся с вами в ближайшее время.
      </p>
      <p v-else-if="store.publicOffer.status === 'declined'" class="mt-6 text-sm text-gray-600">
        Вы отклонили этот оффер.
      </p>
      <p v-else-if="store.publicOffer.status === 'expired'" class="mt-6 text-sm text-orange-600">
        Срок действия оффера истёк.
      </p>
    </template>
  </div>
</template>
