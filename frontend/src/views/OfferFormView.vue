<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useOffersStore } from '@/stores/offers'
import BaseButton from '@/components/base/BaseButton.vue'
import FormField from '@/components/base/FormField.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import { publicOfferLink } from '@/utils/offerLink'

type Step = 'form' | 'preview' | 'sent'

const store = useOffersStore()
const router = useRouter()

const step = ref<Step>('form')
const candidateName = ref('')
const candidateEmail = ref('')
const position = ref('')
const salaryNote = ref('')
const expiresAtDate = ref('')

const errors = ref<Record<string, string>>({})
const isSaving = ref(false)
const isSending = ref(false)
const copied = ref(false)

// Tracked locally rather than read off store.current, which may still hold a
// previously sent offer from an earlier visit to this form in the same
// session — using it here would PATCH that unrelated, already-sent offer.
const draftId = ref<number | null>(null)

const expiresAtIso = computed(() => (expiresAtDate.value ? `${expiresAtDate.value}T23:59:59` : ''))

function validate(): boolean {
  const next: Record<string, string> = {}
  if (!candidateName.value.trim()) next.candidateName = 'Укажите имя кандидата'
  if (!candidateEmail.value.trim()) next.candidateEmail = 'Укажите email кандидата'
  if (!position.value.trim()) next.position = 'Укажите должность'
  if (!expiresAtDate.value) next.expiresAtDate = 'Укажите срок действия оффера'
  errors.value = next
  return Object.keys(next).length === 0
}

async function goToPreview(): Promise<void> {
  if (!validate()) return

  isSaving.value = true
  try {
    const payload = {
      candidate_name: candidateName.value.trim(),
      candidate_email: candidateEmail.value.trim(),
      position: position.value.trim(),
      salary_note: salaryNote.value.trim() || undefined,
      expires_at: expiresAtIso.value,
    }
    if (draftId.value) {
      await store.update(draftId.value, payload)
    } else {
      const offer = await store.create(payload)
      draftId.value = offer.id
    }
    step.value = 'preview'
  } finally {
    isSaving.value = false
  }
}

function editAgain(): void {
  step.value = 'form'
}

async function sendOffer(): Promise<void> {
  if (!draftId.value) return
  isSending.value = true
  try {
    await store.send(draftId.value)
    step.value = 'sent'
  } finally {
    isSending.value = false
  }
}

async function copyLink(): Promise<void> {
  if (!store.current?.public_token) return
  await navigator.clipboard.writeText(publicOfferLink(store.current.public_token))
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}

function goToOffersList(): void {
  router.push({ name: 'offers' })
}
</script>

<template>
  <div class="max-w-xl space-y-4">
    <PageHeader title="Новый оффер" />

    <form v-if="step === 'form'" class="space-y-4 rounded-lg border border-gray-200 bg-white p-6" @submit.prevent="goToPreview">
      <FormField v-model="candidateName" label="Имя кандидата" :error="errors.candidateName" />
      <FormField v-model="candidateEmail" label="Email кандидата" type="email" :error="errors.candidateEmail" />
      <FormField v-model="position" label="Должность" :error="errors.position" />
      <FormField v-model="salaryNote" label="Условия (зарплата, формат работы и т.д.)" />
      <FormField v-model="expiresAtDate" label="Срок действия оффера" type="date" :error="errors.expiresAtDate" />
      <BaseButton type="submit" :loading="isSaving">Далее: превью</BaseButton>
    </form>

    <div v-else-if="step === 'preview' && store.current" class="space-y-4">
      <div class="rounded-lg border border-gray-200 bg-white p-6">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-400">Так увидит кандидат</p>
        <h2 class="mt-2 text-lg font-semibold text-gray-900">{{ store.current.position }}</h2>
        <p class="mt-1 text-sm text-gray-600">Здравствуйте, {{ store.current.candidate_name }}!</p>
        <p v-if="store.current.salary_note" class="mt-3 text-sm text-gray-700">{{ store.current.salary_note }}</p>
        <p class="mt-3 text-xs text-gray-400">
          Оффер действителен до {{ new Date(store.current.expires_at!).toLocaleDateString('ru-RU') }}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <BaseButton variant="secondary" @click="editAgain">Редактировать</BaseButton>
        <BaseButton :loading="isSending" @click="sendOffer">Отправить оффер</BaseButton>
      </div>
    </div>

    <div v-else-if="step === 'sent' && store.current" class="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
      <p class="text-sm font-medium text-green-600">Оффер отправлен</p>
      <p class="text-sm text-gray-600">Публичная ссылка для кандидата:</p>
      <div class="flex items-center gap-3">
        <code class="flex-1 truncate rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-700">
          {{ publicOfferLink(store.current.public_token!) }}
        </code>
        <BaseButton variant="secondary" @click="copyLink">{{ copied ? 'Скопировано ✓' : 'Копировать' }}</BaseButton>
      </div>
      <BaseButton @click="goToOffersList">К списку офферов</BaseButton>
    </div>
  </div>
</template>
