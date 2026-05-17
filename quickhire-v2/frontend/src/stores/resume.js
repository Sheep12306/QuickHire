import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  uploadResume, optimizeResume, diagnoseResume, quickScan,
  generateQuestions, getResumeHistory, getLatestResume,
} from '../api/resume'

export const useResumeStore = defineStore('resume', () => {
  const resumeText = ref('')
  const targetPosition = ref('')
  const optimizationStyle = ref('简洁专业')
  const optimizedResult = ref(null)
  const analysisResult = ref(null)
  const questions = ref(null)
  const resumeHistory = ref([])
  const latestResume = ref(null)

  const isOptimizing = ref(false)
  const isAnalyzing = ref(false)
  const isGenerating = ref(false)

  const hasInput = computed(() => resumeText.value.trim().length > 0)
  const hasOptimized = computed(() => !!optimizedResult.value)
  const hasAnalysis = computed(() => !!analysisResult.value)
  const hasQuestions = computed(() => !!questions.value?.length)

  async function upload(file) {
    const { data } = await uploadResume(file)
    resumeText.value = data.content
    return data
  }

  async function optimize() {
    isOptimizing.value = true
    try {
      const { data } = await optimizeResume({
        resume_text: resumeText.value,
        target_position: targetPosition.value,
        optimization_style: optimizationStyle.value,
      })
      optimizedResult.value = data
      return data
    } finally {
      isOptimizing.value = false
    }
  }

  async function analyze() {
    isAnalyzing.value = true
    try {
      const { data } = await diagnoseResume({
        resume_text: resumeText.value,
        target_position: targetPosition.value,
      })
      analysisResult.value = data
      return data
    } finally {
      isAnalyzing.value = false
    }
  }

  async function scan() {
    const { data } = await quickScan({ resume_text: resumeText.value })
    analysisResult.value = data
    return data
  }

  async function genQuestions(difficulty, types, scope, count) {
    isGenerating.value = true
    try {
      const { data } = await generateQuestions({
        resume_text: resumeText.value,
        difficulty,
        question_types: types,
        scope,
        question_count: count,
      })
      questions.value = data.questions
      return data
    } finally {
      isGenerating.value = false
    }
  }

  async function loadHistory() {
    const { data } = await getResumeHistory()
    resumeHistory.value = data
  }

  async function loadLatest() {
    try {
      const { data } = await getLatestResume()
      latestResume.value = data
      if (data) {
        resumeText.value = data.original_content
        targetPosition.value = data.target_position || ''
      }
    } catch {
      // No resume yet
    }
  }

  function clearOptimized() { optimizedResult.value = null }
  function clearAnalysis() { analysisResult.value = null }
  function clearQuestions() { questions.value = null }
  function reset() {
    resumeText.value = ''
    targetPosition.value = ''
    optimizationStyle.value = '简洁专业'
    optimizedResult.value = null
    analysisResult.value = null
    questions.value = null
  }

  return {
    resumeText, targetPosition, optimizationStyle,
    optimizedResult, analysisResult, questions,
    resumeHistory, latestResume,
    isOptimizing, isAnalyzing, isGenerating,
    hasInput, hasOptimized, hasAnalysis, hasQuestions,
    upload, optimize, analyze, scan, genQuestions,
    loadHistory, loadLatest,
    clearOptimized, clearAnalysis, clearQuestions, reset,
  }
})
