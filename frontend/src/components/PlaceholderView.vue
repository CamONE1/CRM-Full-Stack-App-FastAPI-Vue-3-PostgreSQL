<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-gray-500">
    <h1 class="mb-1 text-lg font-semibold text-gray-900">{{ title }}</h1>
    <p>Страница в разработке — появится на следующих этапах.</p>
  </div>
</template>
