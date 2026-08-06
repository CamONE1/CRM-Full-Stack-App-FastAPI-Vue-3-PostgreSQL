<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps<{
  total: number
  page: number
  pageSize: number
}>()

const emit = defineEmits<{ (e: 'update:page', page: number): void }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
</script>

<template>
  <div class="flex items-center justify-between text-sm text-gray-600">
    <span>Всего: {{ total }}</span>
    <div class="flex items-center gap-2">
      <BaseButton variant="secondary" :disabled="page === 0" @click="emit('update:page', page - 1)">
        Назад
      </BaseButton>
      <span>{{ page + 1 }} / {{ totalPages }}</span>
      <BaseButton variant="secondary" :disabled="page + 1 >= totalPages" @click="emit('update:page', page + 1)">
        Вперёд
      </BaseButton>
    </div>
  </div>
</template>
