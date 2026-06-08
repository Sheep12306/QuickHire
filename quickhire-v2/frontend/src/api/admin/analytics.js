import api from '../index'

export function getConversionFunnel(days = 30) {
  return api.get('/admin/analytics/conversion-funnel', { params: { days } })
}

export function getRetention() {
  return api.get('/admin/analytics/retention')
}

export function getFeatureUsageHeatmap(days = 30) {
  return api.get('/admin/analytics/feature-usage-heatmap', { params: { days } })
}

export function exportReport(metrics, format = 'csv', dateFrom = '', dateTo = '') {
  return api.post('/admin/analytics/export-report', { metrics, format, date_from: dateFrom, date_to: dateTo }, { responseType: 'blob' })
}
