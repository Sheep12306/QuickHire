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
