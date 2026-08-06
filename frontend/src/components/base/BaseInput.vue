<script setup lang="ts">
withDefaults(
  defineProps<{
    type?: string
    placeholder?: string
  }>(),
  { type: 'text' },
)

const model = defineModel<string>({ required: true })
</script>

<template>
  <input
    v-model="model"
    :type="type"
    :placeholder="placeholder"
    class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm"
  />
</template>
