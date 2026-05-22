<template>
  <div class="login-page">
    <NavBar />
    <main class="main-content">
      <div class="login-panel">
        <!-- Decorative side -->
        <div class="panel-decor">
          <div class="decor-bg"></div>
          <div class="decor-content">
            <div class="decor-logo">
              <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
                <rect width="44" height="44" rx="12" fill="rgba(255,255,255,0.2)"/>
                <path d="M12 22.5l7 7 14-14" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h2 class="decor-title">QuickHire</h2>
            <p class="decor-desc">AI 驱动的简历优化与面试教练平台，助你拿下心仪 Offer。</p>
          </div>
        </div>

        <!-- Form side -->
        <div class="panel-form">
          <el-tabs v-model="activeTab" class="login-tabs" stretch>
            <el-tab-pane label="登录" name="login">
              <el-form @submit.prevent="handleLogin" class="auth-form">
                <el-form-item>
                  <el-input
                    v-model="loginForm.credential"
                    placeholder="邮箱或手机号"
                    size="large"
                  >
                    <template #prefix><el-icon><User /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="密码"
                    size="large"
                    show-password
                    @keyup.enter="handleLogin"
                  >
                    <template #prefix><el-icon><Lock /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="large" @click="handleLogin" :loading="loading" class="submit-btn">
                    登 录
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="注册" name="register">
              <el-form @submit.prevent="handleRegister" class="auth-form">
                <el-form-item>
                  <el-input v-model="registerForm.email" placeholder="邮箱（选填）" size="large">
                    <template #prefix><el-icon><Message /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input v-model="registerForm.phone" placeholder="手机号（选填）" size="large">
                    <template #prefix><el-icon><Phone /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input v-model="registerForm.display_name" placeholder="您的称呼" size="large">
                    <template #prefix><el-icon><UserFilled /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" size="large" show-password>
                    <template #prefix><el-icon><Lock /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" size="large" show-password>
                    <template #prefix><el-icon><Lock /></el-icon></template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="large" @click="handleRegister" :loading="loading" class="submit-btn">
                    注 册
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import NavBar from '../components/layout/NavBar.vue'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const activeTab = ref('login')

const loginForm = reactive({ credential: '', password: '' })
const registerForm = reactive({
  email: '', phone: '', display_name: '', password: '', confirmPassword: '',
})

async function handleLogin() {
  if (!loginForm.credential || !loginForm.password) {
    ElMessage.error('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(loginForm.credential, loginForm.password)
    ElMessage.success('登录成功！')
    router.push('/resume-optimizer')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.email && !registerForm.phone) {
    ElMessage.error('请至少填写邮箱或手机号')
    return
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await auth.register({
      email: registerForm.email.trim(),
      phone: registerForm.phone.trim(),
      password: registerForm.password,
      display_name: registerForm.display_name.trim(),
    })
    ElMessage.success('注册成功！')
    router.push('/resume-optimizer')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--bg-page);
}

.main-content {
  padding: 100px 1.5rem 2rem;
  max-width: 880px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
}

/* ── Panel ──────────────────────────────── */
.login-panel {
  display: flex;
  width: 100%;
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
  min-height: 520px;
}

/* ── Decorative side ────────────────────── */
.panel-decor {
  flex: 0 0 38%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  overflow: hidden;
}
.decor-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, var(--green-700) 0%, var(--green-500) 60%, var(--green-400) 100%);
}
.decor-bg::after {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  top: -80px; right: -80px;
}
.decor-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: #fff;
}
.decor-logo {
  margin-bottom: 1.25rem;
}
.decor-title {
  font-size: 1.6rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
  letter-spacing: -0.02em;
}
.decor-desc {
  font-size: 0.9rem;
  opacity: 0.85;
  line-height: 1.6;
}

/* ── Form side ──────────────────────────── */
.panel-form {
  flex: 1;
  padding: 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 1.5rem;
}
.login-tabs :deep(.el-tabs__item) {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-muted);
}
.login-tabs :deep(.el-tabs__item.is-active) {
  color: var(--green-600);
}
.login-tabs :deep(.el-tabs__active-bar) {
  background: var(--green-600);
}

.auth-form {
  margin-top: 0.5rem;
}
.submit-btn {
  width: 100%;
  font-size: 1rem;
  font-weight: 700;
  padding: 12px 0;
  letter-spacing: 0.1em;
}

@media (max-width: 700px) {
  .login-panel {
    flex-direction: column;
  }
  .panel-decor {
    flex: 0 0 auto;
    padding: 2.5rem 1.5rem;
  }
  .decor-desc {
    font-size: 0.85rem;
  }
  .panel-form {
    padding: 1.5rem;
  }
}
</style>
