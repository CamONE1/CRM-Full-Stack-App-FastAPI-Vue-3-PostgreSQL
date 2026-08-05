<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types/auth'

interface NavItem {
  to: string
  label: string
}

interface NavSection {
  title: string
  roles?: UserRole[]
  items: NavItem[]
}

// Sections/pages per PLAN.md page map (§2): Общее / HR / Админ.
const SECTIONS: NavSection[] = [
  {
    title: 'Общее',
    items: [
      { to: '/dashboard', label: 'Дашборд' },
      { to: '/news', label: 'Новости' },
      { to: '/profile', label: 'Профиль' },
    ],
  },
  {
    title: 'HR',
    roles: ['hr', 'admin'],
    items: [
      { to: '/employees', label: 'Сотрудники' },
      { to: '/offers', label: 'Офферы' },
    ],
  },
  {
    title: 'Админ',
    roles: ['admin'],
    items: [{ to: '/users', label: 'Пользователи' }],
  },
]

const authStore = useAuthStore()

const visibleSections = computed(() =>
  SECTIONS.filter((section) => !section.roles || section.roles.includes(authStore.role as UserRole)),
)
</script>

<template>
  <nav class="flex h-full w-60 flex-col gap-6 border-r border-gray-200 bg-white p-4">
    <div class="px-2 text-lg font-semibold text-gray-900">HR-портал</div>
    <div v-for="section in visibleSections" :key="section.title" class="flex flex-col gap-1">
      <span class="px-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
        {{ section.title }}
      </span>
      <RouterLink
        v-for="item in section.items"
        :key="item.to"
        :to="item.to"
        class="rounded-md px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-100"
        active-class="bg-indigo-50 font-medium text-indigo-700"
      >
        {{ item.label }}
      </RouterLink>
    </div>
  </nav>
</template>
