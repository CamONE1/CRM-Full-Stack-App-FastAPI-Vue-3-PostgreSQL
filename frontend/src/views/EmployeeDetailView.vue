<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEmployeesStore } from '@/stores/employees'
import BaseButton from '@/components/base/BaseButton.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const store = useEmployeesStore()

const employeeId = computed(() => Number(route.params.id))

async function load(): Promise<void> {
  await store.fetchById(employeeId.value)
}

onMounted(load)
watch(employeeId, load)
</script>

<template>
  <div class="space-y-4">
    <BaseButton variant="secondary" @click="router.push({ name: 'employees' })">← К списку</BaseButton>

    <div v-if="store.current" class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-lg font-semibold text-gray-900">{{ store.current.full_name }}</h1>
          <p class="text-sm text-gray-500">{{ store.current.position ?? '—' }}</p>
        </div>
        <StatusBadge :variant="store.current.is_active ? 'green' : 'gray'">
          {{ store.current.is_active ? 'Активен' : 'Неактивен' }}
        </StatusBadge>
      </div>

      <dl class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400">Email</dt>
          <dd class="text-sm text-gray-900">{{ store.current.email }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400">Отдел</dt>
          <dd class="text-sm text-gray-900">{{ store.current.department ?? '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400">Телефон</dt>
          <dd class="text-sm text-gray-900">{{ store.current.phone ?? '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400">Telegram</dt>
          <dd class="text-sm text-gray-900">{{ store.current.telegram ?? '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400">Дата найма</dt>
          <dd class="text-sm text-gray-900">{{ store.current.hire_date ?? '—' }}</dd>
        </div>
      </dl>
    </div>

    <div class="rounded-lg border border-dashed border-gray-300 bg-white p-6 text-center text-gray-400">
      Офферы сотрудника появятся на этапе 3.
    </div>
  </div>
</template>
