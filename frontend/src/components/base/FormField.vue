<script setup lang="ts">
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
    <input
      v-model="model"
      :type="type ?? 'text'"
      class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm"
    />
    <span v-if="error" class="mt-1 block text-sm text-red-600">{{ error }}</span>
  </label>
</template>
