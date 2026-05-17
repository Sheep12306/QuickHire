import api from './index'

export function generatePracticeQuestions(data) {
  return api.post('/practice/generate', data)
}

export function savePracticeQuestions(data) {
  return api.post('/practice/save', data)
}

export function browseQuestions(params) {
  return api.get('/practice/browse', { params })
}

export function toggleFavorite(questionId) {
  return api.post(`/practice/${questionId}/favorite`)
}

export function getFavorites() {
  return api.get('/practice/favorites')
}

export function listPositions() {
  return api.get('/practice/positions')
}
