<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/base/BaseButton.vue'
import FormField from '@/components/base/FormField.vue'

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit(): Promise<void> {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    await authStore.login(email.value, password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.push(redirect)
  } catch {
    errorMessage.value = 'Неверный email или пароль'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-svh items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm rounded-lg bg-white p-8 shadow">
      <h1 class="mb-6 text-xl font-semibold text-gray-900">Вход в HR-портал</h1>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <FormField v-model="email" label="Email" type="email" />
        <FormField v-model="password" label="Пароль" type="password" />
        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>
        <BaseButton type="submit" class="w-full" :loading="isSubmitting">Войти</BaseButton>
      </form>
    </div>
  </div>
</template>
