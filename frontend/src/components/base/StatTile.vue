<script setup lang="ts">
defineProps<{ label: string; value: string | number }>()
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-4">
    <div class="text-sm text-gray-500">{{ label }}</div>
    <div class="mt-1 text-2xl font-semibold text-gray-900">{{ value }}</div>
  </div>
</template>
