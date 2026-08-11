<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOffersStore } from '@/stores/offers'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import type { SelectOption } from '@/components/base/BaseSelect.vue'
import type { Offer, OfferStatus } from '@/types/offer'
import { publicOfferLink } from '@/utils/offerLink'
import { OFFER_STATUS_LABELS, OFFER_STATUS_VARIANTS } from '@/utils/offerStatus'

const PAGE_SIZE = 20

const STATUS_OPTIONS: SelectOption[] = [
  { value: '', label: 'Любой статус' },
  ...Object.entries(OFFER_STATUS_LABELS).map(([value, label]) => ({ value, label })),
]

const ARCHIVED_OPTIONS: SelectOption[] = [
  { value: '', label: 'Без архивных' },
  { value: 'true', label: 'Показать архивные' },
]

const COLUMNS = [
  { key: 'candidate_name', label: 'Кандидат' },
  { key: 'position', label: 'Должность' },
  { key: 'status', label: 'Статус' },
  { key: 'expires_at', label: 'Срок действия' },
  { key: 'created_at', label: 'Создан' },
  { key: 'actions', label: 'Действия' },
]

const store = useOffersStore()
const route = useRoute()
const router = useRouter()

const search = ref('')
const status = ref('')
const position = ref('')
const archived = ref('')
const page = ref(0)
const copiedOfferId = ref<number | null>(null)

const positionOptions = computed<SelectOption[]>(() => [
  { value: '', label: 'Любая должность' },
  ...store.positions.map((p) => ({ value: p, label: p })),
])

let searchDebounceHandle: ReturnType<typeof setTimeout> | undefined
// Guards the page-reset watchers below while readFromQuery() assigns filter
// refs from the URL — that assignment must not be mistaken for a user-driven
// filter change that should reset pagination.
let isSyncingFromQuery = false

async function readFromQuery(): Promise<void> {
  isSyncingFromQuery = true
  search.value = typeof route.query.search === 'string' ? route.query.search : ''
  status.value = typeof route.query.status === 'string' ? route.query.status : ''
  position.value = typeof route.query.position === 'string' ? route.query.position : ''
  archived.value = typeof route.query.archived === 'string' ? route.query.archived : ''
  page.value = Number(route.query.page ?? 0) || 0
  await nextTick()
  isSyncingFromQuery = false
}

function writeToQuery(): void {
  router.replace({
    query: {
      search: search.value || undefined,
      status: status.value || undefined,
      position: position.value || undefined,
      archived: archived.value || undefined,
      page: page.value > 0 ? String(page.value) : undefined,
    },
  })
}

function currentParams() {
  return {
    search: search.value || undefined,
    status: (status.value || undefined) as OfferStatus | undefined,
    position: position.value || undefined,
    include_archived: archived.value === 'true',
    offset: page.value * PAGE_SIZE,
    limit: PAGE_SIZE,
  }
}

async function loadOffers(): Promise<void> {
  await store.fetchList(currentParams())
}

function goToPage(next: number): void {
  page.value = next
  writeToQuery()
}

function goToNewOffer(): void {
  router.push({ name: 'offers-new' })
}

async function copyLink(offer: Offer): Promise<void> {
  if (!offer.public_token) return
  await navigator.clipboard.writeText(publicOfferLink(offer.public_token))
  copiedOfferId.value = offer.id
  setTimeout(() => {
    if (copiedOfferId.value === offer.id) copiedOfferId.value = null
  }, 1500)
}

async function archiveOffer(offer: Offer): Promise<void> {
  await store.archive(offer.id)
  await loadOffers()
}

function formatDateTime(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

watch([status, position, archived], () => {
  if (isSyncingFromQuery) return
  page.value = 0
  writeToQuery()
})

watch(search, () => {
  if (isSyncingFromQuery) return
  clearTimeout(searchDebounceHandle)
  searchDebounceHandle = setTimeout(() => {
    page.value = 0
    writeToQuery()
  }, 300)
})

watch(
  () => route.query,
  () => {
    readFromQuery()
    loadOffers()
  },
)

onMounted(() => {
  store.fetchPositions()
  readFromQuery()
  loadOffers()
})
</script>

<template>
  <div class="space-y-4">
    <PageHeader title="Офферы">
      <template #actions>
        <BaseButton @click="goToNewOffer">Новый оффер</BaseButton>
      </template>
    </PageHeader>

    <div class="flex flex-wrap items-center gap-3">
      <div class="w-64">
        <BaseInput v-model="search" placeholder="Поиск по имени или email кандидата" />
      </div>
      <BaseSelect v-model="status" :options="STATUS_OPTIONS" />
      <BaseSelect v-model="position" :options="positionOptions" />
      <BaseSelect v-model="archived" :options="ARCHIVED_OPTIONS" />
    </div>

    <BaseTable :columns="COLUMNS" :rows="store.items" :loading="store.isLoading">
      <template #cell-status="{ row }">
        <StatusBadge :variant="OFFER_STATUS_VARIANTS[row.status as OfferStatus]">
          {{ OFFER_STATUS_LABELS[row.status as OfferStatus] }}
        </StatusBadge>
      </template>

      <template #cell-expires_at="{ row }">
        {{ formatDateTime(row.expires_at) }}
      </template>

      <template #cell-created_at="{ row }">
        {{ formatDateTime(row.created_at) }}
      </template>

      <template #cell-actions="{ row }">
        <div class="flex items-center gap-2">
          <BaseButton v-if="row.public_token" variant="secondary" @click="copyLink(row)">
            {{ copiedOfferId === row.id ? 'Скопировано ✓' : 'Копировать ссылку' }}
          </BaseButton>
          <BaseButton v-if="!row.is_archived" variant="secondary" @click="archiveOffer(row)">
            Архивировать
          </BaseButton>
          <span v-else class="text-xs text-gray-400">В архиве</span>
        </div>
      </template>
    </BaseTable>

    <BasePagination :total="store.total" :page="page" :page-size="PAGE_SIZE" @update:page="goToPage" />
  </div>
</template>
