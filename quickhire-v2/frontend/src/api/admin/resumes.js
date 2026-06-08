import api from '../index'

export function getResumes(params = {}) {
  return api.get('/admin/resumes', { params })
}

export function getResumeDetail(id) {
  return api.get(`/admin/resumes/${id}`)
}

export function getResumeVersions(id) {
  return api.get(`/admin/resumes/${id}/versions`)
}

export function deleteResume(id) {
  return api.delete(`/admin/resumes/${id}`)
}

export function flagResume(id, flagged, flagReason = '') {
  return api.patch(`/admin/resumes/${id}/flag`, { flagged, flag_reason: flagReason })
}
