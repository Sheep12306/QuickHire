<template>
  <nav class="topnav">
    <div class="topnav-inner">
      <router-link to="/" class="topnav-brand">
        <span class="brand-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="#059669"/>
            <path d="M7 14.5l4 4 10-9" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span class="brand-text">QuickHire</span>
      </router-link>

      <div class="topnav-links">
        <router-link v-for="nav in navItems" :key="nav.path" :to="nav.path" class="nav-link" active-class="nav-link--active">
          <el-icon class="nav-icon"><component :is="nav.icon" /></el-icon>
          <span>{{ nav.label }}</span>
        </router-link>
      </div>

      <div class="topnav-actions">
        <template v-if="auth.isLoggedIn">
          <el-avatar :size="32" class="user-avatar">
            {{ (auth.user?.display_name || 'U')[0].toUpperCase() }}
          </el-avatar>
          <span class="user-name">{{ auth.user?.display_name }}</span>
          <router-link to="/profile" class="nav-link">
            <el-icon class="nav-icon"><Setting /></el-icon>
            <span>设置</span>
          </router-link>
          <el-button text type="danger" size="small" @click="handleLogout" class="logout-btn">
            退出
          </el-button>
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
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const navItems = [
  { path: '/', label: '首页', icon: 'HomeFilled' },
  { path: '/resume-optimizer', label: '简历优化', icon: 'Document' },
  { path: '/interview-coach', label: '面试教练', icon: 'Microphone' },
  { path: '/analytics', label: '数据看板', icon: 'TrendCharts' },
  { path: '/practice', label: '面试刷题', icon: 'Collection' },
]

function handleLogout() {
  auth.logout()
  router.push('/')
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

/* Brand */
.topnav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-mark {
  display: flex;
  align-items: center;
}
.brand-text {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--green-700);
  letter-spacing: -0.02em;
}

/* Nav links */
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
.nav-icon {
  font-size: 1.05rem;
}
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

/* Actions */
.topnav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
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
.logout-btn {
  font-weight: 500;
}
</style>
