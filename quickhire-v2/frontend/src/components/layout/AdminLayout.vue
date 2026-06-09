<template>
  <el-container class="admin-layout">
    <el-aside :width="sidebarCollapsed && !isMobile ? '64px' : '220px'" :class="{ 'aside--mobile-open': mobileMenuOpen }">
      <AdminSidebar :collapsed="sidebarCollapsed && !isMobile" :mobile-open="mobileMenuOpen" @close-mobile="mobileMenuOpen = false" />
    </el-aside>

    <!-- Overlay backdrop (mobile) -->
    <div v-if="mobileMenuOpen" class="sidebar-overlay" @click="mobileMenuOpen = false" />

    <el-container>
      <el-header height="56px">
        <AdminTopbar
          :collapsed="sidebarCollapsed"
          :is-mobile="isMobile"
          :mobile-open="mobileMenuOpen"
          @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
          @toggle-mobile="mobileMenuOpen = !mobileMenuOpen"
        />
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
import { ref, onMounted, onUnmounted } from 'vue'
import AdminSidebar from './AdminSidebar.vue'
import AdminTopbar from './AdminTopbar.vue'

const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) mobileMenuOpen.value = false
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>
