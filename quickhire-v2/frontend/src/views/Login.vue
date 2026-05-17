<template>
  <div class="login-page">
    <NavBar />
    <main class="main-content">
      <h1 class="brand-hero">欢迎使用快克简历优化</h1>
      <p class="brand-subtitle">登录或注册以解锁全部功能</p>

      <el-row :gutter="24">
        <!-- Login -->
        <el-col :span="12">
          <div class="login-card">
            <h2 class="login-title">🔑 登录</h2>
            <el-form @submit.prevent="handleLogin">
              <el-form-item>
                <el-input v-model="loginForm.credential" placeholder="邮箱或手机号" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" @click="handleLogin" :loading="loading" style="width:100%">
                  登 录
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <!-- Register -->
        <el-col :span="12">
          <div class="login-card">
            <h2 class="login-title">📝 注册</h2>
            <el-form @submit.prevent="handleRegister">
              <el-form-item>
                <el-input v-model="registerForm.email" placeholder="邮箱（选填）" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.phone" placeholder="手机号（选填）" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.display_name" placeholder="您的称呼" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" size="large" show-password />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" size="large" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" @click="handleRegister" :loading="loading" style="width:100%">
                  注 册
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
      </el-row>
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
.login-page { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 800px; margin: 0 auto; }
.brand-hero { font-size: 2rem; font-weight: 700; color: #0f766e; text-align: center; margin-bottom: 0.5rem; }
.brand-subtitle { font-size: 1rem; color: #0d9488; text-align: center; margin-bottom: 2rem; }
.login-card { background: #fff; border-radius: 16px; padding: 2rem 1.8rem; border: 1px solid #ccfbf1; box-shadow: 0 4px 24px rgba(15, 118, 110, 0.06); }
.login-title { font-size: 1.3rem; font-weight: 700; color: #0f766e; margin-bottom: 1.2rem; text-align: center; }
</style>
