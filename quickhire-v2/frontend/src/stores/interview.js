import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { coachStart, coachScore, coachSummary, getAnswers } from '../api/interview'

export const useInterviewStore = defineStore('interview', () => {
  const phase = ref('setup')  // setup | answering | feedback | finished
  const questions = ref([])
  const currentIndex = ref(0)
  const answers = ref([])     // { number, question, answer, score, feedback }
  const currentFeedback = ref(null)
  const summary = ref(null)
  const isLoading = ref(false)
  const answerHistory = ref([])

  const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
  const totalQuestions = computed(() => questions.value.length)
  const isLastQuestion = computed(() => currentIndex.value >= totalQuestions.value - 1)

  const avgScore = computed(() => {
    if (!answers.value.length) return 0
    const sum = answers.value.reduce((s, a) => s + (a.score || 0), 0)
    return Math.round(sum / answers.value.length)
  })

  async function start(interviewType, difficulty, count) {
    isLoading.value = true
    try {
      const { data } = await coachStart({
        interview_type: interviewType,
        difficulty,
        question_count: count,
      })
      questions.value = data.questions || []
      currentIndex.value = 0
      answers.value = []
      currentFeedback.value = null
      summary.value = null
      phase.value = 'answering'
    } finally {
      isLoading.value = false
    }
  }

  async function submitAnswer(questionText, userAnswer) {
    isLoading.value = true
    try {
      const { data } = await coachScore({
        question: questionText,
        user_answer: userAnswer,
      })
      currentFeedback.value = data
      answers.value.push({
        number: currentIndex.value + 1,
        question: questionText,
        answer: userAnswer,
        score: data.overall_score,
        feedback: data,
      })
      phase.value = 'feedback'
    } finally {
      isLoading.value = false
    }
  }

  function prevQuestion() {
    if (currentIndex.value > 0) {
      currentIndex.value--
      // Show previous answer's feedback if available
      const prevAnswer = answers.value.find(a => a.number === currentIndex.value + 1)
      currentFeedback.value = prevAnswer?.feedback || null
      phase.value = 'feedback'
    }
  }

  function nextQuestion() {
    if (isLastQuestion.value) {
      phase.value = 'finished'
      return
    }
    currentIndex.value++
    // If this question was already answered, show its feedback
    const existing = answers.value.find(a => a.number === currentIndex.value + 1)
    if (existing?.feedback) {
      currentFeedback.value = existing.feedback
      phase.value = 'feedback'
    } else {
      currentFeedback.value = null
      phase.value = 'answering'
    }
  }

  async function finishInterview() {
    isLoading.value = true
    try {
      const { data } = await coachSummary({
        session_qa: answers.value.map(a => ({
          question: a.question,
          answer: a.answer,
          score: a.score,
        })),
      })
      summary.value = data
      phase.value = 'finished'
    } finally {
      isLoading.value = false
    }
  }

  function restart() {
    phase.value = 'setup'
    questions.value = []
    currentIndex.value = 0
    answers.value = []
    currentFeedback.value = null
    summary.value = null
  }

  async function loadHistory() {
    const { data } = await getAnswers()
    answerHistory.value = data
  }

  return {
    phase, questions, currentIndex, answers, currentFeedback, summary,
    isLoading, answerHistory,
    currentQuestion, totalQuestions, isLastQuestion, avgScore,
    start, submitAnswer, prevQuestion, nextQuestion, finishInterview, restart,
    loadHistory,
  }
})
