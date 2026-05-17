<template>
  <nav class="topnav">
    <div class="topnav-brand">
      <span class="brand-icon">📝</span>
      <span class="brand-text">快克简历优化</span>
    </div>

    <div class="topnav-links">
      <router-link to="/" class="nav-link" active-class="nav-link--active">首页</router-link>
      <router-link to="/resume-optimizer" class="nav-link" active-class="nav-link--active">简历优化</router-link>
      <router-link to="/interview-coach" class="nav-link" active-class="nav-link--active">面试教练</router-link>
      <router-link to="/analytics" class="nav-link" active-class="nav-link--active">数据看板</router-link>
      <router-link to="/practice" class="nav-link" active-class="nav-link--active">面试刷题</router-link>
    </div>

    <div class="topnav-actions">
      <template v-if="auth.isLoggedIn">
        <span class="user-avatar">👤 {{ auth.user?.display_name }}</span>
        <router-link to="/profile" class="nav-link">个人中心</router-link>
        <el-button text type="danger" size="small" @click="handleLogout">退出</el-button>
      </template>
      <template v-else>
        <el-button text @click="$router.push('/login')">🔐 登录</el-button>
        <el-button type="primary" size="small" @click="$router.push('/login')">📝 注册</el-button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.topnav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 999;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.75rem 2rem; height: 56px;
  background: rgba(240, 253, 250, 0.95);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #ccfbf1;
  box-shadow: 0 1px 8px rgba(15, 118, 110, 0.06);
}
.topnav-brand { display: flex; align-items: center; gap: 0.5rem; }
.brand-icon { font-size: 1.5rem; }
.brand-text { font-size: 1.1rem; font-weight: 700; color: #0f766e; }
.topnav-links { display: flex; align-items: center; gap: 0.25rem; }
.nav-link {
  color: #5b8a87; font-size: 0.85rem; font-weight: 500;
  text-decoration: none; padding: 0.4rem 0.75rem; border-radius: 8px;
  transition: all 0.2s ease;
}
.nav-link:hover { background: #f0fdfa; color: #0f766e; }
.nav-link--active { background: #ccfbf1; color: #0f766e; font-weight: 600; }
.topnav-actions { display: flex; align-items: center; gap: 0.5rem; }
.user-avatar { font-size: 0.85rem; color: #0f766e; font-weight: 600; }
</style>
