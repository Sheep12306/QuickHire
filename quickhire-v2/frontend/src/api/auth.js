import api from './index'

export function login(credential, password) {
  return api.post('/auth/login', { credential, password })
}

export function register(data) {
  return api.post('/auth/register', data)
}

export function getMe() {
  return api.get('/auth/me')
}

export function sendCode(email) {
  return api.post('/auth/send-code', { email })
}

export function verifyCodeLogin(email, code) {
  return api.post('/auth/verify-code-login', { email, code })
}
