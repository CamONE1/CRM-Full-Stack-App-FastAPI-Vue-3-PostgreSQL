<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useStatsStore } from '@/stores/stats'
import { useNewsStore } from '@/stores/news'
import { useEmployeesStore } from '@/stores/employees'
import PageHeader from '@/components/base/PageHeader.vue'
import StatTile from '@/components/base/StatTile.vue'
import EmptyState from '@/components/base/EmptyState.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { OFFER_STATUS_LABELS, OFFER_STATUS_VARIANTS } from '@/utils/offerStatus'
import type { OfferStatus } from '@/types/offer'

const authStore = useAuthStore()
const statsStore = useStatsStore()
const newsStore = useNewsStore()
const employeesStore = useEmployeesStore()

const isHrAdmin = computed(() => authStore.role === 'hr' || authStore.role === 'admin')

const isLoading = ref(true)
const loadError = ref(false)

// Fixed lifecycle order, light -> dark indigo ramp. Validated with the dataviz
// skill's CVD/contrast checker (see components/charts/BarChart.vue) — reusing
// StatusBadge's 5 status colors here failed that check (orange/red collide).
const OFFER_STATUS_ORDER: OfferStatus[] = ['draft', 'sent', 'accepted', 'declined', 'expired']
const OFFER_FUNNEL_RAMP = ['#818cf8', '#6366f1', '#4f46e5', '#3730a3', '#1e1b4b']

const offersFunnelCategories = computed(() => OFFER_STATUS_ORDER.map((s) => OFFER_STATUS_LABELS[s]))
const offersFunnelValues = computed(() => OFFER_STATUS_ORDER.map((s) => statsStore.data?.offers.by_status[s] ?? 0))

const departmentCategories = computed(() => Object.keys(statsStore.data?.employees.by_department ?? {}))
const departmentValues = computed(() => Object.values(statsStore.data?.employees.by_department ?? {}))

onMounted(async () => {
  try {
    if (isHrAdmin.value) {
      await statsStore.fetch()
    } else {
      await Promise.all([employeesStore.fetchMyProfile(), newsStore.fetchList({ limit: 5 })])
    }
  } catch {
    loadError.value = true
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Дашборд" />

    <div v-if="isLoading" class="text-sm text-gray-500">Загрузка…</div>
    <p v-else-if="loadError" class="text-sm text-red-600">Не удалось загрузить дашборд</p>

    <template v-else-if="isHrAdmin && statsStore.data">
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatTile label="Офферы всего" :value="statsStore.data.offers.total" />
        <StatTile label="Сотрудники всего" :value="statsStore.data.employees.total" />
        <StatTile label="Активные сотрудники" :value="statsStore.data.employees.active" />
        <StatTile label="Неактивные сотрудники" :value="statsStore.data.employees.inactive" />
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <h2 class="mb-2 text-sm font-semibold text-gray-900">Воронка офферов</h2>
          <BarChart
            v-if="statsStore.data.offers.total > 0"
            :categories="offersFunnelCategories"
            :values="offersFunnelValues"
            :colors="OFFER_FUNNEL_RAMP"
          />
          <EmptyState v-else message="Пока нет офферов" />
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <h2 class="mb-2 text-sm font-semibold text-gray-900">Сотрудники по отделам</h2>
          <BarChart v-if="departmentCategories.length > 0" :categories="departmentCategories" :values="departmentValues" />
          <EmptyState v-else message="Нет данных по отделам" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <h2 class="mb-2 text-sm font-semibold text-gray-900">Последние офферы</h2>
          <ul v-if="statsStore.data.recent_offers.length" class="divide-y divide-gray-100">
            <li v-for="offer in statsStore.data.recent_offers" :key="offer.id">
              <RouterLink
                :to="{ name: 'offers', query: { search: offer.candidate_email } }"
                class="flex items-center justify-between gap-2 py-2 text-sm hover:bg-gray-50"
              >
                <span class="text-gray-900">{{ offer.candidate_name }} · {{ offer.position }}</span>
                <StatusBadge :variant="OFFER_STATUS_VARIANTS[offer.status]">
                  {{ OFFER_STATUS_LABELS[offer.status] }}
                </StatusBadge>
              </RouterLink>
            </li>
          </ul>
          <EmptyState v-else message="Пока нет офферов" />
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <h2 class="mb-2 text-sm font-semibold text-gray-900">Последние новости</h2>
          <ul v-if="statsStore.data.recent_news.length" class="divide-y divide-gray-100">
            <li v-for="item in statsStore.data.recent_news" :key="item.id">
              <RouterLink
                :to="{ name: 'news-detail', params: { id: item.id } }"
                class="block py-2 text-sm text-gray-900 hover:bg-gray-50"
              >
                {{ item.title }}
              </RouterLink>
            </li>
          </ul>
          <EmptyState v-else message="Пока нет новостей" />
        </div>
      </div>
    </template>

    <template v-else>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-lg border border-gray-200 bg-white p-6">
          <h2 class="mb-3 text-sm font-semibold text-gray-900">Мой профиль</h2>
          <template v-if="employeesStore.myProfile">
            <p class="text-base font-medium text-gray-900">{{ employeesStore.myProfile.full_name }}</p>
            <p class="text-sm text-gray-500">
              {{ employeesStore.myProfile.position ?? '—' }} · {{ employeesStore.myProfile.department ?? '—' }}
            </p>
            <RouterLink :to="{ name: 'profile' }" class="mt-3 inline-block text-sm text-indigo-600 hover:text-indigo-500">
              Редактировать профиль →
            </RouterLink>
          </template>
          <EmptyState v-else message="К вашей учётной записи не привязан профиль сотрудника" />
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-4">
          <h2 class="mb-2 text-sm font-semibold text-gray-900">Последние новости</h2>
          <ul v-if="newsStore.items.length" class="divide-y divide-gray-100">
            <li v-for="item in newsStore.items" :key="item.id">
              <RouterLink
                :to="{ name: 'news-detail', params: { id: item.id } }"
                class="block py-2 text-sm text-gray-900 hover:bg-gray-50"
              >
                {{ item.title }}
              </RouterLink>
            </li>
          </ul>
          <EmptyState v-else message="Пока нет новостей" />
        </div>
      </div>
    </template>
  </div>
</template>
