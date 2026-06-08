import api from '../index'

export function getApiCallLogs(params = {}) {
  return api.get('/admin/logs/api-calls', { params })
}

export function getErrorLogs(params = {}) {
  return api.get('/admin/logs/errors', { params })
}

export function getCostStats(days = 30) {
  return api.get('/admin/logs/cost-stats', { params: { days } })
}

export function getRateLimitConfig() {
  return api.get('/admin/logs/rate-limit-config')
}

export function updateRateLimitConfig(config) {
  return api.put('/admin/logs/rate-limit-config', config)
}
