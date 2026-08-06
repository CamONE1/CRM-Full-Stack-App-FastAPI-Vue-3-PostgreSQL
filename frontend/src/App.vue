<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'

const route = useRoute()
const layout = computed(() => (route.meta.layout === 'blank' ? BlankLayout : AppLayout))
</script>

<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>
