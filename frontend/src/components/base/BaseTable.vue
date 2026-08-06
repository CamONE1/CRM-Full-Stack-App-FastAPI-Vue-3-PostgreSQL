<script setup lang="ts" generic="T extends Record<string, unknown>">
interface Column {
  key: string
  label: string
}

defineProps<{
  columns: Column[]
  rows: T[]
  loading?: boolean
  emptyText?: string
}>()

defineEmits<{ (e: 'row-click', row: T): void }>()
</script>

<template>
  <div class="overflow-x-auto rounded-lg border border-gray-200 bg-white">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-if="loading">
          <td :colspan="columns.length" class="px-4 py-6 text-center text-sm text-gray-400">Загрузка…</td>
        </tr>
        <tr v-else-if="rows.length === 0">
          <td :colspan="columns.length" class="px-4 py-6 text-center text-sm text-gray-400">
            {{ emptyText ?? 'Нет данных' }}
          </td>
        </tr>
        <tr
          v-for="(row, index) in rows"
          :key="index"
          class="cursor-pointer hover:bg-gray-50"
          @click="$emit('row-click', row)"
        >
          <td v-for="col in columns" :key="col.key" class="px-4 py-2 text-sm text-gray-700">
            <slot :name="`cell-${col.key}`" :row="row">{{ row[col.key] }}</slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
