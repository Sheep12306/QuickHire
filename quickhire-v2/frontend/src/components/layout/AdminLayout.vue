<template>
  <el-container class="admin-layout">
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'">
      <AdminSidebar :collapsed="sidebarCollapsed" />
    </el-aside>
    <el-container>
      <el-header height="56px">
        <AdminTopbar @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      </el-header>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import AdminSidebar from './AdminSidebar.vue'
import AdminTopbar from './AdminTopbar.vue'

const sidebarCollapsed = ref(false)
</script>
