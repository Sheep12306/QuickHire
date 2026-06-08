import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getMe, verifyCodeLogin as apiVerifyCodeLogin } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => {
    const role = user.value?.role || 'user'
    return ['super_admin', 'operator', 'viewer'].includes(role)
  })
  const isSuperAdmin = computed(() => user.value?.role === 'super_admin')

  async function initialize() {
    if (token.value) {
      try {
        const { data } = await getMe()
        user.value = data
      } catch {
        logout()
      }
    }
  }

  async function login(credential, password) {
    const { data } = await apiLogin(credential, password)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', token.value)
    return data
  }

  async function loginByCode(email, code) {
    const { data } = await apiVerifyCodeLogin(email, code)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', token.value)
    return data
  }

  async function register(form) {
    const { data } = await apiRegister(form)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', token.value)
    return data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, isAdmin, isSuperAdmin, initialize, login, loginByCode, register, logout }
})
