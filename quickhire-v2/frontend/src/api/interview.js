import api from './index'

export function coachStart(data) {
  return api.post('/interview/coach/start', data)
}

export function coachScore(data) {
  return api.post('/interview/coach/score', data)
}

export function coachSummary(data) {
  return api.post('/interview/coach/summary', data)
}

export function reinforcement() {
  return api.post('/interview/reinforcement')
}

export function getAnswers() {
  return api.get('/interview/answers')
}

export function getQuestionBanks() {
  return api.get('/interview/question-banks')
}
