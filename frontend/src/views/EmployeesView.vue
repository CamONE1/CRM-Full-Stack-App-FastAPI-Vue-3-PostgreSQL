<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useEmployeesStore } from '@/stores/employees'
import * as employeesApi from '@/api/employees'
import { downloadCsv } from '@/utils/csv'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import type { Employee } from '@/types/employee'

const PAGE_SIZE = 20
const STATUS_OPTIONS = [
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
const router = useRouter()

const search = ref('')
const position = ref('')
const status = ref('')
const page = ref(0)
const isExporting = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(store.total / PAGE_SIZE)))

let searchDebounceHandle: ReturnType<typeof setTimeout> | undefined

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

function goToEmployee(row: Employee): void {
  router.push({ name: 'employee-detail', params: { id: row.id } })
}

async function exportCsv(): Promise<void> {
  isExporting.value = true
  try {
    const { items } = await employeesApi.fetchEmployees({ ...currentParams(), offset: 0, limit: 1000 })
    downloadCsv(
      'employees.csv',
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
  page.value = 0
  loadEmployees()
})

watch(search, () => {
  clearTimeout(searchDebounceHandle)
  searchDebounceHandle = setTimeout(() => {
    page.value = 0
    loadEmployees()
  }, 300)
})

watch(page, () => {
  loadEmployees()
})

onMounted(() => {
  store.fetchPositions()
  loadEmployees()
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold text-gray-900">Сотрудники</h1>
      <BaseButton variant="secondary" :loading="isExporting" @click="exportCsv">Экспорт CSV</BaseButton>
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <input
        v-model="search"
        type="text"
        placeholder="Поиск по имени или email"
        class="w-64 rounded-md border-0 px-3 py-2 text-sm text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
      />
      <select
        v-model="position"
        class="rounded-md border-0 px-3 py-2 text-sm text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
      >
        <option value="">Любая должность</option>
        <option v-for="p in store.positions" :key="p" :value="p">{{ p }}</option>
      </select>
      <select
        v-model="status"
        class="rounded-md border-0 px-3 py-2 text-sm text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
      >
        <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>

    <BaseTable :columns="COLUMNS" :rows="store.items" :loading="store.isLoading" @row-click="goToEmployee">
      <template #cell-status="{ row }">
        <StatusBadge :variant="row.is_active ? 'green' : 'gray'">
          {{ row.is_active ? 'Активен' : 'Неактивен' }}
        </StatusBadge>
      </template>
    </BaseTable>

    <div class="flex items-center justify-between text-sm text-gray-600">
      <span>Всего: {{ store.total }}</span>
      <div class="flex items-center gap-2">
        <BaseButton variant="secondary" :disabled="page === 0" @click="page--">Назад</BaseButton>
        <span>{{ page + 1 }} / {{ totalPages }}</span>
        <BaseButton variant="secondary" :disabled="page + 1 >= totalPages" @click="page++">Вперёд</BaseButton>
      </div>
    </div>
  </div>
</template>
