<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="flex items-center justify-between">
    <h1 class="text-lg font-semibold text-gray-900">{{ title }}</h1>
    <slot name="actions" />
  </div>
</template>
