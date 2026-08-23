import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ForgotPasswordPage from '@/pages/ForgotPasswordPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import TasksPage from '@/pages/TasksPage.vue'
import GoalsPage from '@/pages/GoalsPage.vue'
import RoadmapPage from '@/pages/RoadmapPage.vue'
import FinancePage from '@/pages/FinancePage.vue'
import MoviesPage from '@/pages/MoviesPage.vue'
import BooksPage from '@/pages/BooksPage.vue'
import PlacesPage from '@/pages/PlacesPage.vue'
import BackupPage from '@/pages/BackupPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import CalendarPage from '@/pages/CalendarPage.vue'
import IdeasPage from '@/pages/IdeasPage.vue'
import MentorPage from '@/pages/MentorPage.vue'
import BioTrackerPage from '@/pages/BioTrackerPage.vue'
import SkillsPage from '@/pages/SkillsPage.vue'

const routes = [
  { path: '/login', component: LoginPage, meta: { guest: true } },
  { path: '/register', component: RegisterPage, meta: { guest: true } },
  { path: '/forgot-password', component: ForgotPasswordPage, meta: { guest: true } },
  { path: '/', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/ideas', component: IdeasPage, meta: { requiresAuth: true } },
  { path: '/mentor', component: MentorPage, meta: { requiresAuth: true } },
  { path: '/bio', component: BioTrackerPage, meta: { requiresAuth: true } },
  { path: '/skills', component: SkillsPage, meta: { requiresAuth: true } },
  { path: '/tasks', component: TasksPage, meta: { requiresAuth: true } },
  { path: '/goals', component: GoalsPage, meta: { requiresAuth: true } },
  { path: '/roadmap', component: RoadmapPage, meta: { requiresAuth: true } },
  { path: '/finance', component: FinancePage, meta: { requiresAuth: true } },
  { path: '/movies', component: MoviesPage, meta: { requiresAuth: true } },
  { path: '/books', component: BooksPage, meta: { requiresAuth: true } },
  { path: '/places', component: PlacesPage, meta: { requiresAuth: true } },
  { path: '/backup', component: BackupPage, meta: { requiresAuth: true } },
  { path: '/profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/calendar', name: 'Calendar', component: CalendarPage, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router