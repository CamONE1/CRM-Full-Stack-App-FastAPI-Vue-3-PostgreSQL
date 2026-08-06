<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'green' | 'red' | 'gray' | 'blue' | 'orange'
  }>(),
  { variant: 'gray' },
)

const VARIANT_CLASSES: Record<string, string> = {
  green: 'bg-green-50 text-green-700 ring-green-600/20',
  red: 'bg-red-50 text-red-700 ring-red-600/20',
  gray: 'bg-gray-50 text-gray-600 ring-gray-500/10',
  blue: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  orange: 'bg-orange-50 text-orange-700 ring-orange-600/20',
}
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="VARIANT_CLASSES[variant]"
  >
    <slot />
  </span>
</template>
