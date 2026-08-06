<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useEmployeesStore } from '@/stores/employees'
import BaseButton from '@/components/base/BaseButton.vue'
import FormField from '@/components/base/FormField.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import StatusBadge from '@/components/base/StatusBadge.vue'

const store = useEmployeesStore()

const phone = ref('')
const telegram = ref('')
const isSaving = ref(false)
const successMessage = ref('')
const loadError = ref(false)

function resetForm(): void {
  phone.value = store.myProfile?.phone ?? ''
  telegram.value = store.myProfile?.telegram ?? ''
}

async function handleSubmit(): Promise<void> {
  isSaving.value = true
  successMessage.value = ''
  try {
    await store.updateMyProfile({ phone: phone.value, telegram: telegram.value })
    successMessage.value = 'Профиль обновлён'
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  try {
    await store.fetchMyProfile()
    resetForm()
  } catch {
    loadError.value = true
  }
})

watch(() => store.myProfile, resetForm)
</script>

<template>
  <div class="max-w-xl space-y-4">
    <PageHeader title="Мой профиль" />

    <div v-if="store.myProfile" class="rounded-lg border border-gray-200 bg-white p-6">
      <div class="flex items-start justify-between">
        <div>
          <p class="text-base font-medium text-gray-900">{{ store.myProfile.full_name }}</p>
          <p class="text-sm text-gray-500">{{ store.myProfile.position ?? '—' }} · {{ store.myProfile.department ?? '—' }}</p>
        </div>
        <StatusBadge :variant="store.myProfile.is_active ? 'green' : 'gray'">
          {{ store.myProfile.is_active ? 'Активен' : 'Неактивен' }}
        </StatusBadge>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="handleSubmit">
        <FormField v-model="phone" label="Телефон" />
        <FormField v-model="telegram" label="Telegram" />
        <div class="flex items-center gap-3">
          <BaseButton type="submit" :loading="isSaving">Сохранить</BaseButton>
          <span v-if="successMessage" class="text-sm text-green-600">{{ successMessage }}</span>
        </div>
      </form>
    </div>

    <p v-else-if="loadError" class="text-sm text-red-600">
      К вашей учётной записи не привязан профиль сотрудника.
    </p>
    <p v-else class="text-sm text-gray-500">Загрузка…</p>
  </div>
</template>
