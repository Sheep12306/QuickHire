<template>
  <div class="admin-sidebar">
    <router-link to="/" class="logo">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" class="logo-svg">
        <rect width="28" height="28" rx="8" fill="#059669"/>
        <path d="M7 14.5l4 4 10-9" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span v-if="!collapsed" class="logo-text">QuickHire</span>
    </router-link>
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :router="true"
      background-color="transparent"
    >
      <el-menu-item index="/admin/dashboard">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>

      <el-menu-item index="/admin/users">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <el-menu-item index="/admin/resumes">
        <el-icon><Document /></el-icon>
        <template #title>简历管理</template>
      </el-menu-item>

      <el-sub-menu index="logs">
        <template #title>
          <el-icon><Monitor /></el-icon>
          <span>日志中心</span>
        </template>
        <el-menu-item index="/admin/logs/api">API调用日志</el-menu-item>
        <el-menu-item index="/admin/logs/errors">错误日志</el-menu-item>
        <el-menu-item index="/admin/logs/costs">成本统计</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/admin/analytics/operations">
        <el-icon><TrendCharts /></el-icon>
        <template #title>运营分析</template>
      </el-menu-item>

      <el-sub-menu index="content">
        <template #title>
          <el-icon><EditPen /></el-icon>
          <span>内容管理</span>
        </template>
        <el-menu-item index="/admin/content/templates">简历模板</el-menu-item>
        <el-menu-item index="/admin/content/prompts">Prompt模板</el-menu-item>
        <el-menu-item index="/admin/content/announcements">公告管理</el-menu-item>
        <el-menu-item index="/admin/content/help">帮助中心</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="packages">
        <template #title>
          <el-icon><ShoppingBag /></el-icon>
          <span>套餐订单</span>
        </template>
        <el-menu-item index="/admin/packages/plans">套餐管理</el-menu-item>
        <el-menu-item index="/admin/packages/orders">订单管理</el-menu-item>
        <el-menu-item index="/admin/packages/memberships">会员管理</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/admin/system" v-if="userRole === 'super_admin'">
        <el-icon><Setting /></el-icon>
        <template #title>系统设置</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import {
  DataAnalysis, User, Document, Monitor, TrendCharts,
  EditPen, ShoppingBag, Setting,
} from '@element-plus/icons-vue'

defineProps({
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
const auth = useAuthStore()

const activeMenu = computed(() => route.path)
const userRole = computed(() => auth.user?.role || '')
</script>
