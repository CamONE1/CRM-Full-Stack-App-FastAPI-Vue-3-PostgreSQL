<script setup lang="ts">
export interface SelectOption {
  value: string
  label: string
}

defineProps<{
  options: SelectOption[]
}>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <select
    v-model="model"
    class="rounded-md border-0 px-3 py-2 text-sm text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
  >
    <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
  </select>
</template>
