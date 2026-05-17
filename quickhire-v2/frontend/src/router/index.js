import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/resume-optimizer',
    name: 'ResumeOptimizer',
    component: () => import('../views/ResumeOptimizer.vue'),
  },
  {
    path: '/interview-coach',
    name: 'InterviewCoach',
    component: () => import('../views/InterviewCoach.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('../views/Analytics.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/practice',
    name: 'PracticeCenter',
    component: () => import('../views/PracticeCenter.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
