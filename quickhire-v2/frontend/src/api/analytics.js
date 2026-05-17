import api from './index'

export function getDashboard() {
  return api.get('/analytics/dashboard')
}

export function addApplication(data) {
  return api.post('/analytics/applications', data)
}

export function getApplications() {
  return api.get('/analytics/applications')
}

export function updateApplicationStatus(id, status) {
  return api.patch(`/analytics/applications/${id}?status=${status}`)
}

export function generateMonthlyReport() {
  return api.post('/analytics/monthly-report')
}
