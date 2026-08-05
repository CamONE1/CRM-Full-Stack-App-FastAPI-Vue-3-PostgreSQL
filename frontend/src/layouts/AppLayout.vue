<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'
import BaseButton from '@/components/base/BaseButton.vue'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout(): void {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex min-h-svh bg-gray-50">
    <AppSidebar />
    <div class="flex flex-1 flex-col">
      <header class="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
        <span class="text-sm text-gray-500">{{ authStore.user?.email }} · {{ authStore.role }}</span>
        <BaseButton variant="secondary" @click="handleLogout">Выйти</BaseButton>
      </header>
      <main class="flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
