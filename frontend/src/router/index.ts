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
    // Layout wrapping the route's component; omit for the default (sidebar) layout.
    layout?: 'blank'
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
      meta: { public: true, layout: 'blank' },
    },
    {
      path: '/403',
      name: 'forbidden',
      component: () => import('@/views/ForbiddenView.vue'),
      meta: { public: true, layout: 'blank' },
    },
    {
      path: '/offer/:token',
      name: 'offer-public',
      component: () => import('@/views/OfferPublicView.vue'),
      meta: { public: true, layout: 'blank' },
    },
    { path: '/', redirect: { name: 'dashboard' } },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/news', name: 'news', component: PlaceholderView, props: { title: 'Новости' } },
    { path: '/news/:id', name: 'news-detail', component: PlaceholderView, props: { title: 'Новость' } },
    {
      path: '/news/manage',
      name: 'news-manage',
      component: PlaceholderView,
      props: { title: 'Управление новостями' },
      meta: { roles: HR_ADMIN },
    },
    { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
    {
      path: '/employees',
      name: 'employees',
      component: () => import('@/views/EmployeesView.vue'),
      meta: { roles: HR_ADMIN },
    },
    {
      path: '/employees/:id',
      name: 'employee-detail',
      component: () => import('@/views/EmployeeDetailView.vue'),
      meta: { roles: HR_ADMIN },
    },
    {
      path: '/offers',
      name: 'offers',
      component: () => import('@/views/OffersView.vue'),
      meta: { roles: HR_ADMIN },
    },
    {
      path: '/offers/new',
      name: 'offers-new',
      component: () => import('@/views/OfferFormView.vue'),
      meta: { roles: HR_ADMIN },
    },
    {
      path: '/users',
      name: 'users',
      component: PlaceholderView,
      props: { title: 'Пользователи' },
      meta: { roles: ['admin'] },
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
