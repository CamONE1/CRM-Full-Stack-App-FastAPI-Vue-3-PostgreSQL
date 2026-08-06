<script setup lang="ts">
import BaseInput from './BaseInput.vue'

defineProps<{
  label: string
  type?: string
  error?: string
}>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <label class="block">
    <span class="mb-1 block text-sm font-medium text-gray-700">{{ label }}</span>
    <BaseInput v-model="model" :type="type" />
    <span v-if="error" class="mt-1 block text-sm text-red-600">{{ error }}</span>
  </label>
</template>
