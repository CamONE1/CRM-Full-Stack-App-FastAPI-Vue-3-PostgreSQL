<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<template>
  <div
    class="flex min-h-32 items-center justify-center rounded-lg border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500"
  >
    {{ message }}
  </div>
</template>
