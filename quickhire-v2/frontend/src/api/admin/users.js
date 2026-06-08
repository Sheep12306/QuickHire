import api from '../index'

export function getUsers(params = {}) {
  return api.get('/admin/users', { params })
}

export function exportUsers(format = 'csv') {
  return api.get('/admin/users/export', { params: { format } })
}

export function getUserDetail(id) {
  return api.get(`/admin/users/${id}`)
}

export function banUser(id, reason = '', durationHours = 0) {
  return api.patch(`/admin/users/${id}/ban`, { reason, duration_hours: durationHours })
}

export function unbanUser(id) {
  return api.patch(`/admin/users/${id}/unban`)
}

export function changeUserRole(id, role) {
  return api.patch(`/admin/users/${id}/role`, { role })
}

export function resetUserPassword(id, newPassword) {
  return api.post(`/admin/users/${id}/reset-password`, { new_password: newPassword })
}

export function getUserNotes(id) {
  return api.get(`/admin/users/${id}/notes`)
}

export function addUserNote(id, note) {
  return api.post(`/admin/users/${id}/notes`, { note })
}

export function getUserAuditLog(id, params = {}) {
  return api.get(`/admin/users/${id}/audit-log`, { params })
}
