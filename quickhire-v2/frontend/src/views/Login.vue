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
          <!-- Guest login (primary) -->
          <div class="guest-section">
            <div class="guest-icon">
              <el-icon :size="26"><MagicStick /></el-icon>
            </div>
            <h2 class="guest-title">无需注册，立即体验</h2>
            <p class="guest-desc">AI 简历优化 · 面试教练 · 面试刷题</p>
            <el-button
              type="primary"
              size="large"
              class="guest-btn"
              :loading="guestLoading"
              @click="handleGuestLogin"
            >
              游客登录 · 立即体验
            </el-button>
          </div>

          <!-- Divider -->
          <div class="account-divider">
            <span>或使用账号登录</span>
          </div>

          <!-- Account login (secondary, smaller) -->
          <div class="account-section">
            <el-button
              v-if="!showAccountForm"
              text
              type="primary"
              class="account-toggle"
              @click="showAccountForm = true"
            >
              账号登录 / 注册
            </el-button>

            <template v-else>
              <el-tabs v-model="activeTab" class="login-tabs" stretch>
                <el-tab-pane label="登录" name="login">
                  <!-- Password mode -->
                  <el-form v-if="loginMode === 'password'" @submit.prevent="handleLogin" class="auth-form">
                    <el-form-item>
                      <el-input
                        v-model="loginForm.credential"
                        placeholder="邮箱或手机号"
                      >
                        <template #prefix><el-icon><User /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input
                        v-model="loginForm.password"
                        type="password"
                        placeholder="密码"
                        show-password
                        @keyup.enter="handleLogin"
                      >
                        <template #prefix><el-icon><Lock /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="handleLogin" :loading="loading" class="submit-btn">
                        登 录
                      </el-button>
                    </el-form-item>
                    <p class="mode-toggle">
                      <el-button link type="primary" @click="loginMode = 'code'">验证码登录</el-button>
                    </p>
                  </el-form>

                  <!-- Verification code mode -->
                  <el-form v-else @submit.prevent="handleCodeLogin" class="auth-form">
                    <el-form-item>
                      <el-input
                        v-model="codeForm.email"
                        placeholder="邮箱"
                      >
                        <template #prefix><el-icon><Message /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input
                        v-model="codeForm.code"
                        placeholder="验证码"
                        @keyup.enter="handleCodeLogin"
                      >
                        <template #prefix><el-icon><Key /></el-icon></template>
                        <template #suffix>
                          <el-button
                            link
                            type="primary"
                            :disabled="countdown > 0"
                            @click="sendVerificationCode"
                            style="font-size:0.85rem"
                          >
                            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                          </el-button>
                        </template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="handleCodeLogin" :loading="loading" class="submit-btn">
                        登 录
                      </el-button>
                    </el-form-item>
                    <p class="mode-toggle">
                      <el-button link type="primary" @click="loginMode = 'password'">密码登录</el-button>
                    </p>
                  </el-form>
                </el-tab-pane>

                <el-tab-pane label="注册" name="register">
                  <el-form @submit.prevent="handleRegister" class="auth-form">
                    <el-form-item>
                      <el-input v-model="registerForm.email" placeholder="邮箱（选填）">
                        <template #prefix><el-icon><Message /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input v-model="registerForm.phone" placeholder="手机号（选填）">
                        <template #prefix><el-icon><Phone /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input v-model="registerForm.display_name" placeholder="您的称呼">
                        <template #prefix><el-icon><UserFilled /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" show-password>
                        <template #prefix><el-icon><Lock /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" show-password>
                        <template #prefix><el-icon><Lock /></el-icon></template>
                      </el-input>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="handleRegister" :loading="loading" class="submit-btn">
                        注 册
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>
              </el-tabs>
            </template>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { sendCode as apiSendCode } from '../api/auth'
import { ElMessage } from 'element-plus'
import NavBar from '../components/layout/NavBar.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const guestLoading = ref(false)
const showAccountForm = ref(false)
const activeTab = ref('login')
const loginMode = ref('password')
const countdown = ref(0)

const loginForm = reactive({ credential: '', password: '' })
const codeForm = reactive({ email: '', code: '' })
const registerForm = reactive({
  email: '', phone: '', display_name: '', password: '', confirmPassword: '',
})

async function handleGuestLogin() {
  guestLoading.value = true
  try {
    await auth.guestLogin()
    ElMessage.success('已进入体验模式')
    const redirect = route.query.redirect
    router.push(redirect || '/resume-optimizer')
  } finally {
    guestLoading.value = false
  }
}

async function handleLogin() {
  if (!loginForm.credential || !loginForm.password) {
    ElMessage.error('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(loginForm.credential, loginForm.password)
    ElMessage.success('登录成功！')
    const redirect = route.query.redirect
    router.push(redirect || (auth.isAdmin ? '/admin/dashboard' : '/resume-optimizer'))
  } finally {
    loading.value = false
  }
}

async function sendVerificationCode() {
  if (!codeForm.email) {
    ElMessage.error('请输入邮箱')
    return
  }
  try {
    await apiSendCode(codeForm.email)
    ElMessage.success('验证码已发送，请查收邮件')
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch { /* error handled by interceptor */ }
}

async function handleCodeLogin() {
  if (!codeForm.email || !codeForm.code) {
    ElMessage.error('请输入邮箱和验证码')
    return
  }
  loading.value = true
  try {
    await auth.loginByCode(codeForm.email, codeForm.code)
    ElMessage.success('登录成功！')
    const redirect2 = route.query.redirect
    router.push(redirect2 || (auth.isAdmin ? '/admin/dashboard' : '/resume-optimizer'))
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
    const redirect3 = route.query.redirect
    router.push(redirect3 || '/resume-optimizer')
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

/* ── Guest login (primary) ──────────────── */
.guest-section {
  text-align: center;
}
.guest-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--green-500), var(--green-600));
  box-shadow: 0 8px 20px rgba(5, 150, 105, 0.25);
}
.guest-title {
  font-size: 1.35rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.guest-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0 0 1.5rem;
}
.guest-btn {
  width: 100%;
  max-width: 320px;
  font-size: 1.05rem;
  font-weight: 700;
  padding: 14px 0;
  letter-spacing: 0.05em;
  border-radius: var(--radius-md);
}

/* ── Account login (secondary) ──────────── */
.account-divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.75rem 0 0.75rem;
  color: var(--text-muted);
  font-size: 0.8rem;
}
.account-divider::before,
.account-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-light);
}

.account-section {
  text-align: center;
}
.account-toggle {
  font-size: 0.9rem;
  font-weight: 500;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
}
.login-tabs :deep(.el-tabs__item) {
  font-size: 0.9rem;
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
  margin-top: 0.25rem;
}
.auth-form :deep(.el-input__wrapper) {
  padding: 1px 11px;
}
.auth-form :deep(.el-input__inner) {
  font-size: 0.9rem;
}
.submit-btn {
  width: 100%;
  font-size: 0.95rem;
  font-weight: 700;
  padding: 10px 0;
  letter-spacing: 0.1em;
}

.mode-toggle {
  text-align: right;
  margin: 0;
}

@media (max-width: 700px) {
  .login-panel {
    flex-direction: column;
    min-height: auto;
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
  .main-content {
    padding: 80px 1rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 70px 0.75rem 1rem;
  }
  .panel-decor {
    display: none;
  }
  .decor-title { font-size: 1.3rem; }
  .panel-form {
    padding: 1.25rem 1rem;
  }
  .guest-title { font-size: 1.2rem; }
  .login-tabs :deep(.el-tabs__item) {
    font-size: 0.85rem;
  }
}
</style>
