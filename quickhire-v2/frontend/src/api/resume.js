import api from './index'

export function uploadResume(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/resume/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function optimizeResume(data) {
  return api.post('/resume/optimize', data)
}

export function diagnoseResume(data) {
  return api.post('/resume/diagnose', data)
}

export function quickScan(data) {
  return api.post('/resume/quick-scan', data)
}

export function generateQuestions(data) {
  return api.post('/resume/questions', data)
}

export function getResumeHistory() {
  return api.get('/resume/history')
}

export function getLatestResume() {
  return api.get('/resume/latest')
}

export function setCurrentVersion(id) {
  return api.patch(`/resume/${id}/set-current`)
}
