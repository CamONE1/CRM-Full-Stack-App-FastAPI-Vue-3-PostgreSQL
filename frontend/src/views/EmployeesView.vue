<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEmployeesStore } from '@/stores/employees'
import * as employeesApi from '@/api/employees'
import { downloadCsv } from '@/utils/csv'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import type { SelectOption } from '@/components/base/BaseSelect.vue'
import type { Employee } from '@/types/employee'

const PAGE_SIZE = 20
const STATUS_OPTIONS: SelectOption[] = [
  { value: '', label: 'Любой статус' },
  { value: 'true', label: 'Активен' },
  { value: 'false', label: 'Неактивен' },
]

const COLUMNS = [
  { key: 'full_name', label: 'ФИО' },
  { key: 'email', label: 'Email' },
  { key: 'position', label: 'Должность' },
  { key: 'department', label: 'Отдел' },
  { key: 'phone', label: 'Телефон' },
  { key: 'status', label: 'Статус' },
]

const store = useEmployeesStore()
const route = useRoute()
const router = useRouter()

const search = ref('')
const position = ref('')
const status = ref('')
const page = ref(0)
const isExporting = ref(false)

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
  position.value = typeof route.query.position === 'string' ? route.query.position : ''
  status.value = typeof route.query.status === 'string' ? route.query.status : ''
  page.value = Number(route.query.page ?? 0) || 0
  await nextTick()
  isSyncingFromQuery = false
}

function writeToQuery(): void {
  router.replace({
    query: {
      search: search.value || undefined,
      position: position.value || undefined,
      status: status.value || undefined,
      page: page.value > 0 ? String(page.value) : undefined,
    },
  })
}

function currentParams() {
  return {
    search: search.value || undefined,
    position: position.value || undefined,
    is_active: status.value === '' ? undefined : status.value === 'true',
    offset: page.value * PAGE_SIZE,
    limit: PAGE_SIZE,
  }
}

async function loadEmployees(): Promise<void> {
  await store.fetchList(currentParams())
}

function goToPage(next: number): void {
  page.value = next
  writeToQuery()
}

function goToEmployee(row: Employee): void {
  router.push({ name: 'employee-detail', params: { id: row.id } })
}

function csvFilename(): string {
  const date = new Date().toISOString().slice(0, 10)
  const parts = ['employees', date]
  if (status.value === 'true') parts.push('active')
  else if (status.value === 'false') parts.push('inactive')
  if (position.value) parts.push(slugify(position.value))
  return `${parts.join('_')}.csv`
}

function slugify(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
}

async function exportCsv(): Promise<void> {
  isExporting.value = true
  try {
    const { items } = await employeesApi.fetchEmployees({ ...currentParams(), offset: 0, limit: 1000 })
    downloadCsv(
      csvFilename(),
      ['ФИО', 'Email', 'Должность', 'Отдел', 'Телефон', 'Telegram', 'Статус', 'Дата найма'],
      items.map((e) => [
        e.full_name,
        e.email,
        e.position,
        e.department,
        e.phone,
        e.telegram,
        e.is_active ? 'Активен' : 'Неактивен',
        e.hire_date,
      ]),
    )
  } finally {
    isExporting.value = false
  }
}

watch([position, status], () => {
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
    loadEmployees()
  },
)

onMounted(() => {
  store.fetchPositions()
  readFromQuery()
  loadEmployees()
})
</script>

<template>
  <div class="space-y-4">
    <PageHeader title="Сотрудники">
      <template #actions>
        <BaseButton variant="secondary" :loading="isExporting" @click="exportCsv">Экспорт CSV</BaseButton>
      </template>
    </PageHeader>

    <div class="flex flex-wrap items-center gap-3">
      <div class="w-64">
        <BaseInput v-model="search" placeholder="Поиск по имени или email" />
      </div>
      <BaseSelect v-model="position" :options="positionOptions" />
      <BaseSelect v-model="status" :options="STATUS_OPTIONS" />
    </div>

    <BaseTable :columns="COLUMNS" :rows="store.items" :loading="store.isLoading" @row-click="goToEmployee">
      <template #cell-status="{ row }">
        <StatusBadge :variant="row.is_active ? 'green' : 'gray'">
          {{ row.is_active ? 'Активен' : 'Неактивен' }}
        </StatusBadge>
      </template>
    </BaseTable>

    <BasePagination :total="store.total" :page="page" :page-size="PAGE_SIZE" @update:page="goToPage" />
  </div>
</template>
