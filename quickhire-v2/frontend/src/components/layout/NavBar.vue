<template>
  <div class="navbar-root">
    <nav class="topnav">
    <div class="topnav-inner">
      <!-- Left: hamburger + brand -->
      <div class="topnav-left">
        <button
          class="hamburger"
          :class="{ 'hamburger--open': mobileMenuOpen }"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-label="mobileMenuOpen ? '关闭菜单' : '打开菜单'"
        >
          <span></span><span></span><span></span>
        </button>

        <router-link to="/" class="topnav-brand">
          <span class="brand-mark" :class="{ 'brand-mark--hidden': !auth.isLoggedIn }">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="#059669"/>
              <path d="M7 14.5l4 4 10-9" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="brand-text">QuickHire</span>
        </router-link>
      </div>

      <!-- Desktop nav links -->
      <div class="topnav-links desktop-only">
        <router-link v-for="nav in navItems" :key="nav.path" :to="nav.path" class="nav-link" active-class="nav-link--active">
          <el-icon class="nav-icon"><component :is="nav.icon" /></el-icon>
          <span>{{ nav.label }}</span>
        </router-link>
      </div>

      <!-- Right: desktop actions + share -->
      <div class="topnav-right">
        <div class="topnav-actions desktop-only">
          <template v-if="auth.isLoggedIn">
            <el-dropdown trigger="click">
              <div class="user-dropdown-trigger">
                <el-avatar :size="32" class="user-avatar">
                  {{ (auth.user?.display_name || 'U')[0].toUpperCase() }}
                </el-avatar>
                <span class="user-name">{{ auth.user?.display_name }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="auth.isAdmin" @click="$router.push('/admin/dashboard')">
                    <el-icon><Monitor /></el-icon>
                    <span style="margin-left:6px">后台管理</span>
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/profile')">
                    <el-icon><Setting /></el-icon>
                    <span style="margin-left:6px">个人设置</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    <span style="margin-left:6px">退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button class="btn-login" @click="$router.push('/login')">
              <el-icon style="margin-right:4px"><User /></el-icon>
              登录
            </el-button>
            <el-button type="primary" size="small" @click="$router.push('/login')" class="btn-register">
              <el-icon style="margin-right:4px"><EditPen /></el-icon>
              注册
            </el-button>
          </template>
        </div>

        <button class="share-btn" @click="handleShare" aria-label="分享">
          <el-icon :size="18"><Share /></el-icon>
        </button>
      </div>
    </div>

  </nav>

  <!-- Left drawer menu — outside <nav> so fixed positioning works correctly -->
  <div class="mobile-drawer" :class="{ 'mobile-drawer--open': mobileMenuOpen }">
    <!-- Login/Register at top (not logged in) -->
    <div v-if="!auth.isLoggedIn" class="mobile-auth-top">
      <el-button type="primary" size="large" @click="$router.push('/login'); mobileMenuOpen = false" class="mobile-auth-btn">
        <el-icon style="margin-right:6px"><User /></el-icon>
        登录 / 注册
      </el-button>
    </div>

    <router-link v-for="nav in navItems" :key="nav.path" :to="nav.path" class="mobile-nav-link" active-class="mobile-nav-link--active" @click="mobileMenuOpen = false">
      <el-icon class="nav-icon"><component :is="nav.icon" /></el-icon>
      <span>{{ nav.label }}</span>
    </router-link>

    <!-- User area (logged in) -->
    <div v-if="auth.isLoggedIn" class="mobile-user-section">
      <div class="mobile-user-info">
        <el-avatar :size="36" class="user-avatar">
          {{ (auth.user?.display_name || 'U')[0].toUpperCase() }}
        </el-avatar>
        <div>
          <div class="mobile-user-name">{{ auth.user?.display_name }}</div>
        </div>
      </div>
      <router-link v-if="auth.isAdmin" to="/admin/dashboard" class="mobile-nav-link" @click="mobileMenuOpen = false">
        <el-icon class="nav-icon"><Monitor /></el-icon>
        <span>后台管理</span>
      </router-link>
      <router-link to="/profile" class="mobile-nav-link" @click="mobileMenuOpen = false">
        <el-icon class="nav-icon"><Setting /></el-icon>
        <span>设置</span>
      </router-link>
      <el-button text type="danger" @click="handleLogout" class="mobile-logout-btn">
        <el-icon style="margin-right:6px"><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/', label: '首页', icon: 'HomeFilled' },
  { path: '/resume-optimizer', label: '简历优化', icon: 'Document' },
  { path: '/interview-coach', label: '面试教练', icon: 'Microphone' },
  { path: '/analytics', label: '数据看板', icon: 'TrendCharts' },
  { path: '/practice', label: '面试刷题', icon: 'Collection' },
]

function handleLogout() {
  auth.logout()
  mobileMenuOpen = false
  router.push('/')
}

async function handleShare() {
  const url = window.location.href
  const title = 'QuickHire — AI 简历优化与面试教练'

  if (navigator.share) {
    try {
      await navigator.share({ title, url })
    } catch { /* user cancelled */ }
  } else {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制到剪贴板')
  }
}
</script>

<style scoped>
.topnav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 999;
  height: 60px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
}

.topnav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

/* ── Left ─────────────────────────────────── */
.topnav-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Brand */
.topnav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-mark { display: flex; align-items: center; }
.brand-text {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--green-700);
  letter-spacing: -0.02em;
}

/* Nav links (desktop) */
.topnav-links {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  padding: 0.4rem 0.7rem;
  border-radius: var(--radius-sm);
  transition: color var(--duration-fast) var(--ease-out),
              background var(--duration-fast) var(--ease-out);
  position: relative;
}
.nav-icon { font-size: 1.05rem; }
.nav-link:hover {
  color: var(--green-700);
  background: var(--green-50);
}
.nav-link--active {
  color: var(--green-700);
  font-weight: 600;
  background: var(--green-50);
}
.nav-link--active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: var(--green-600);
  border-radius: 2px;
}

/* ── Right ────────────────────────────────── */
.topnav-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.topnav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
.user-avatar {
  background: linear-gradient(135deg, var(--green-500), var(--green-600));
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.user-name {
  font-size: 0.85rem;
  color: var(--text-primary);
  font-weight: 600;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.btn-login {
  font-weight: 500;
  border-radius: var(--radius-sm);
}
.btn-register {
  border-radius: var(--radius-sm);
  font-weight: 600;
}
/* ── Share button ─────────────────────────── */
.share-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--green-50);
  color: var(--green-600);
  border-radius: 50%;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out);
  flex-shrink: 0;
}
.share-btn:hover {
  background: var(--green-100);
  transform: scale(1.08);
}

/* ── Hamburger ────────────────────────────── */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  z-index: 1001;
}
.hamburger span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text-primary);
  border-radius: 2px;
  transition: all 0.3s var(--ease-out);
  transform-origin: center;
}
.hamburger--open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger--open span:nth-child(2) {
  opacity: 0;
  transform: scaleX(0);
}
.hamburger--open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* ── Root wrapper ────────────────────────── */
.navbar-root {
  position: relative;
}

/* ════════════════════════════════════════════
   Mobile left drawer
   ════════════════════════════════════════════ */
.mobile-drawer {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  height: 100dvh;
  width: 68vw;
  max-width: 260px;
  z-index: 998;
  background: #fff;
  box-shadow: 2px 0 32px rgba(0, 0, 0, 0.15);
  will-change: transform;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 72px 0.85rem 1.5rem;
  transform: translateX(-100%);
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-drawer--open {
  transform: translateX(0);
}

.mobile-drawer :deep(.nav-icon) { font-size: 1.1rem; }

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  padding: 0.75rem 0.75rem;
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out);
  flex-shrink: 0;
}
.mobile-nav-link:hover { background: var(--green-50); }
.mobile-nav-link--active {
  color: var(--green-700);
  font-weight: 700;
  background: var(--green-50);
}

/* Auth at top of menu */
.mobile-auth-top {
  padding-bottom: 0.75rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}
.mobile-auth-btn {
  width: 100%;
  font-weight: 600;
  border-radius: var(--radius-md);
}

/* User section at bottom of menu */
.mobile-user-section {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex-shrink: 0;
}
.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.5rem;
}
.mobile-user-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
}
.mobile-logout-btn {
  width: 100%;
  justify-content: flex-start;
  padding: 0.75rem 0.75rem;
  font-size: 0.9rem;
  border-radius: var(--radius-md);
}

/* ════════════════════════════════════════════
   Mobile responsive
   ════════════════════════════════════════════ */
@media (max-width: 768px) {
  .hamburger { display: flex; }

  .desktop-only { display: none !important; }

  .topnav-inner { padding: 0 1rem; }

  /* Hide brand SVG when not logged in, keep text */
  .brand-mark--hidden { display: none; }
  .brand-text { font-size: 1rem; }
}
</style>
