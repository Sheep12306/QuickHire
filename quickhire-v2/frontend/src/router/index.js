import { createRouter, createWebHistory } from 'vue-router'
import { getMe } from '../api/auth'

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

  // ── Admin Routes ───────────────────────────────────────────
  {
    path: '/admin',
    component: () => import('../components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/DashboardHome.vue'),
        meta: { title: '管理仪表盘' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/UserList.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'users/:id',
        name: 'AdminUserDetail',
        component: () => import('../views/admin/UserDetail.vue'),
        meta: { title: '用户详情' },
      },
      {
        path: 'resumes',
        name: 'AdminResumes',
        component: () => import('../views/admin/ResumeRecords.vue'),
        meta: { title: '简历管理' },
      },
      {
        path: 'resumes/:id',
        name: 'AdminResumeDetail',
        component: () => import('../views/admin/ResumeDetail.vue'),
        meta: { title: '简历详情' },
      },
      {
        path: 'logs/api',
        name: 'AdminApiLogs',
        component: () => import('../views/admin/ApiLogs.vue'),
        meta: { title: 'API调用日志' },
      },
      {
        path: 'logs/errors',
        name: 'AdminErrorLogs',
        component: () => import('../views/admin/ErrorLogs.vue'),
        meta: { title: '错误日志' },
      },
      {
        path: 'logs/costs',
        name: 'AdminCostStats',
        component: () => import('../views/admin/CostStats.vue'),
        meta: { title: '成本统计' },
      },
      {
        path: 'analytics/operations',
        name: 'AdminOpsAnalytics',
        component: () => import('../views/admin/OperationsAnalytics.vue'),
        meta: { title: '运营分析' },
      },
      {
        path: 'content/templates',
        name: 'AdminTemplates',
        component: () => import('../views/admin/TemplateManager.vue'),
        meta: { title: '模板管理' },
      },
      {
        path: 'content/prompts',
        name: 'AdminPrompts',
        component: () => import('../views/admin/PromptManager.vue'),
        meta: { title: 'Prompt管理' },
      },
      {
        path: 'content/announcements',
        name: 'AdminAnnouncements',
        component: () => import('../views/admin/AnnouncementManager.vue'),
        meta: { title: '公告管理' },
      },
      {
        path: 'content/help',
        name: 'AdminHelp',
        component: () => import('../views/admin/HelpManager.vue'),
        meta: { title: '帮助管理' },
      },
      {
        path: 'packages/plans',
        name: 'AdminPackages',
        component: () => import('../views/admin/PackageManager.vue'),
        meta: { title: '套餐管理' },
      },
      {
        path: 'packages/orders',
        name: 'AdminOrders',
        component: () => import('../views/admin/OrderManager.vue'),
        meta: { title: '订单管理' },
      },
      {
        path: 'packages/memberships',
        name: 'AdminMemberships',
        component: () => import('../views/admin/MembershipManager.vue'),
        meta: { title: '会员管理' },
      },
      {
        path: 'system',
        name: 'AdminSystem',
        component: () => import('../views/admin/SystemSettings.vue'),
        meta: { title: '系统设置', roles: ['super_admin'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  // Mobile: redirect landing to resume optimizer
  if (to.path === '/' && window.innerWidth <= 768) {
    next('/resume-optimizer')
    return
  }

  const token = localStorage.getItem('token')

  // User routes requiring auth
  if (to.meta.requiresAuth && !token) {
    next('/login?redirect=' + encodeURIComponent(to.fullPath))
    return
  }

  // Admin routes
  if (to.meta.requiresAdmin) {
    if (!token) {
      next('/login?redirect=' + encodeURIComponent(to.fullPath))
      return
    }

    // Fetch user if not loaded yet (page refresh)
    let role = null
    try {
      const { useAuthStore } = await import('../stores/auth')
      const auth = useAuthStore()
      if (!auth.user) {
        const { data } = await getMe()
        auth.user = data
      }
      role = auth.user?.role || 'user'
    } catch {
      localStorage.removeItem('token')
      next('/login')
      return
    }

    const adminRoles = ['super_admin', 'operator', 'viewer']
    if (!adminRoles.includes(role)) {
      next('/')
      return
    }

    // Check route-specific role requirements
    if (to.meta.roles && !to.meta.roles.includes(role)) {
      next('/admin/dashboard')
      return
    }
  }

  // Redirect logged-in users away from login
  if (to.path === '/login' && token) {
    const redirect = to.query.redirect || '/'
    // Admin users go to admin dashboard
    try {
      const { useAuthStore } = await import('../stores/auth')
      const auth = useAuthStore()
      if (auth.isAdmin) {
        next(redirect.startsWith('/admin') ? redirect : '/admin/dashboard')
        return
      }
    } catch {}
    next(redirect !== '/login' ? redirect : '/')
    return
  }

  next()
})

export default router
