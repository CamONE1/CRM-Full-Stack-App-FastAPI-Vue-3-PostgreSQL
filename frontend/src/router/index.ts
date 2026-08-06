import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PlaceholderView from '@/components/PlaceholderView.vue'
import type { UserRole } from '@/types/auth'

declare module 'vue-router' {
  interface RouteMeta {
    // Skips the auth guard entirely (login, 403).
    public?: boolean
    // Roles allowed to access the route; omit to allow any authenticated role.
    roles?: UserRole[]
  }
}

const HR_ADMIN: UserRole[] = ['hr', 'admin']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/403',
      name: 'forbidden',
      component: () => import('@/views/ForbiddenView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        { path: '', redirect: { name: 'dashboard' } },
        { path: 'dashboard', name: 'dashboard', component: PlaceholderView, props: { title: 'Дашборд' } },
        { path: 'news', name: 'news', component: PlaceholderView, props: { title: 'Новости' } },
        { path: 'news/:id', name: 'news-detail', component: PlaceholderView, props: { title: 'Новость' } },
        {
          path: 'news/manage',
          name: 'news-manage',
          component: PlaceholderView,
          props: { title: 'Управление новостями' },
          meta: { roles: HR_ADMIN },
        },
        { path: 'profile', name: 'profile', component: PlaceholderView, props: { title: 'Мой профиль' } },
        {
          path: 'employees',
          name: 'employees',
          component: PlaceholderView,
          props: { title: 'Сотрудники' },
          meta: { roles: HR_ADMIN },
        },
        {
          path: 'employees/:id',
          name: 'employee-detail',
          component: PlaceholderView,
          props: { title: 'Карточка сотрудника' },
          meta: { roles: HR_ADMIN },
        },
        {
          path: 'offers',
          name: 'offers',
          component: PlaceholderView,
          props: { title: 'Офферы' },
          meta: { roles: HR_ADMIN },
        },
        {
          path: 'offers/new',
          name: 'offers-new',
          component: PlaceholderView,
          props: { title: 'Новый оффер' },
          meta: { roles: HR_ADMIN },
        },
        {
          path: 'users',
          name: 'users',
          component: PlaceholderView,
          props: { title: 'Пользователи' },
          meta: { roles: ['admin'] },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (!authStore.isReady) {
    await authStore.restoreSession()
  }

  if (to.meta.public) {
    if (to.name === 'login' && authStore.isAuthenticated) {
      return { name: 'dashboard' }
    }
    return true
  }

  if (!authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.roles && !to.meta.roles.includes(authStore.role as UserRole)) {
    return { name: 'forbidden' }
  }

  return true
})

export default router
