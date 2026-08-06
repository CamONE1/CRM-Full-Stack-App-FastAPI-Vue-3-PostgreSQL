<script setup lang="ts">
import { useRouter } from 'vue-router'
import BaseButton from '@/components/base/BaseButton.vue'

const router = useRouter()
</script>

<template>
  <div class="flex min-h-svh flex-col items-center justify-center gap-4 bg-gray-50 px-4 text-center">
    <h1 class="text-3xl font-semibold text-gray-900">403</h1>
    <p class="text-gray-600">У вас нет доступа к этой странице.</p>
    <BaseButton @click="router.back()">Назад</BaseButton>
  </div>
</template>
