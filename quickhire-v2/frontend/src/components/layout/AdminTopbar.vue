<template>
  <div class="admin-topbar">
    <el-icon class="collapse-btn" @click="$emit('toggleSidebar')">
      <Fold v-if="!collapsed" />
      <Expand v-else />
    </el-icon>

    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="spacer" />

    <!-- Theme toggle -->
    <el-tooltip :content="theme.isDark ? '切换浅色模式' : '切换深色模式'" placement="bottom">
      <el-button :icon="theme.isDark ? Sunny : Moon" circle @click="theme.toggle" text />
    </el-tooltip>

    <!-- Back to main site -->
    <el-tooltip content="返回主站" placement="bottom">
      <el-button icon="HomeFilled" circle @click="$router.push('/')" text />
    </el-tooltip>

    <!-- User -->
    <el-dropdown trigger="click">
      <div class="user-info">
        <el-avatar :size="32">{{ (auth.user?.display_name || 'A')[0] }}</el-avatar>
        <span style="margin-left:8px">{{ auth.user?.display_name || '管理员' }}</span>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="$router.push('/profile')">个人设置</el-dropdown-item>
          <el-dropdown-item @click="$router.push('/')">返回主站</el-dropdown-item>
          <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useThemeStore } from '../../stores/theme'
import { Fold, Expand, Sunny, Moon } from '@element-plus/icons-vue'

defineEmits(['toggleSidebar'])
const props = defineProps({ collapsed: { type: Boolean, default: false } })

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const currentTitle = computed(() => route.meta.title || '')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
