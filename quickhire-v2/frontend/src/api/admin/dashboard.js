import api from '../index'

export function getDashboardOverview() {
  return api.get('/admin/dashboard/overview')
}

export function getTrends(days = 7) {
  return api.get('/admin/dashboard/trends', { params: { days } })
}

export function getAlerts() {
  return api.get('/admin/dashboard/alerts')
}

export function getFeatureRanking(days = 30) {
  return api.get('/admin/dashboard/feature-ranking', { params: { days } })
}

export function getRecentActivities(limit = 20) {
  return api.get('/admin/dashboard/recent-activities', { params: { limit } })
}
