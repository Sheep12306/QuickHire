<template>
  <div class="coach-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">🎤 AI 面试教练</h1>

      <!-- Setup Phase -->
      <div v-if="store.phase === 'setup'" class="setup-card">
        <h2>开始模拟面试</h2>
        <el-form>
          <el-form-item label="面试类型">
            <el-select v-model="interviewType" style="width:200px">
              <el-option label="综合面" value="综合面" />
              <el-option label="技术面" value="技术面" />
              <el-option label="HR面" value="HR面" />
            </el-select>
          </el-form-item>
          <el-form-item label="难度">
            <el-select v-model="difficulty" style="width:200px">
              <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
            </el-select>
          </el-form-item>
          <el-form-item label="题目数量">
            <el-input-number v-model="questionCount" :min="3" :max="10" />
          </el-form-item>
          <el-button type="primary" size="large" @click="store.start(interviewType, difficulty, questionCount)" :loading="store.isLoading">
            开始面试
          </el-button>
        </el-form>
      </div>

      <!-- Answering Phase -->
      <div v-if="store.phase === 'answering'" class="question-area">
        <div class="progress-text">第 {{ store.currentIndex + 1 }} / {{ store.totalQuestions }} 题</div>
        <el-progress :percentage="Math.round((store.currentIndex + 1) / store.totalQuestions * 100)" :show-text="false" />

        <div class="question-card">
          <h3>{{ store.currentQuestion?.question || store.currentQuestion }}</h3>
          <p v-if="store.currentQuestion?.context" class="context">{{ store.currentQuestion.context }}</p>
        </div>

        <el-input
          v-model="userAnswer"
          type="textarea"
          :rows="5"
          placeholder="请输入你的回答..."
          size="large"
        />
        <el-button type="primary" size="large" @click="handleSubmit" :loading="store.isLoading" style="margin-top:1rem">
          提交答案
        </el-button>
      </div>

      <!-- Feedback Phase -->
      <div v-if="store.phase === 'feedback' && store.currentFeedback" class="feedback-area">
        <h3>📊 评分反馈</h3>
        <div class="score-row">
          <div class="score-circle" :class="scoreGrade(store.currentFeedback.overall_score)">
            {{ store.currentFeedback.overall_score }}
          </div>
          <span>综合评分</span>
        </div>

        <div v-if="store.currentFeedback.dimensions" class="dimensions">
          <div v-for="(v, k) in store.currentFeedback.dimensions" :key="k" class="dim-row">
            <span class="dim-label">{{ k }}</span>
            <el-progress :percentage="v.score || v" :color="dimColor(v.score || v)" />
          </div>
        </div>

        <div v-if="store.currentFeedback.strengths?.length">
          <h4>✅ 优点</h4>
          <ul><li v-for="s in store.currentFeedback.strengths" :key="s">{{ s }}</li></ul>
        </div>
        <div v-if="store.currentFeedback.weaknesses?.length">
          <h4>⚠️ 不足</h4>
          <ul><li v-for="w in store.currentFeedback.weaknesses" :key="w">{{ w }}</li></ul>
        </div>
        <div v-if="store.currentFeedback.improved_answer">
          <h4>💡 优化答案</h4>
          <p class="improved">{{ store.currentFeedback.improved_answer }}</p>
        </div>

        <div class="feedback-actions">
          <el-button v-if="store.currentIndex > 0" size="large" @click="store.prevQuestion()">← 上一题</el-button>
          <el-button type="primary" size="large" @click="store.nextQuestion()">
            {{ store.isLastQuestion ? '完成面试' : '下一题 →' }}
          </el-button>
        </div>
      </div>

      <!-- Finished Phase -->
      <div v-if="store.phase === 'finished'" class="finished-area">
        <h3>🎉 面试结束</h3>
        <p>平均得分：<strong>{{ store.avgScore }} 分</strong></p>

        <div v-if="!store.summary">
          <el-button type="primary" @click="store.finishInterview()" :loading="store.isLoading">
            🤖 AI 生成面试总结
          </el-button>
        </div>

        <div v-if="store.summary" class="summary-card">
          <div v-if="store.summary.overall_evaluation">
            <h4>综合评价</h4>
            <p>{{ store.summary.overall_evaluation }}</p>
          </div>
          <div v-if="store.summary.strengths?.length">
            <h4>✅ 优势</h4>
            <ul><li v-for="s in store.summary.strengths" :key="s">{{ s }}</li></ul>
          </div>
          <div v-if="store.summary.weaknesses?.length">
            <h4>⚠️ 待改进</h4>
            <ul><li v-for="w in store.summary.weaknesses" :key="w">{{ w }}</li></ul>
          </div>
        </div>

        <el-button size="large" @click="store.restart()" style="margin-top:1rem">🔄 重新开始</el-button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useInterviewStore } from '../stores/interview'
import NavBar from '../components/layout/NavBar.vue'

const store = useInterviewStore()
const userAnswer = ref('')
const interviewType = ref('综合面')
const difficulty = ref('中等')
const questionCount = ref(5)

const difficulties = ['入门', '基础', '中等', '面试高频', '深度深挖']

function handleSubmit() {
  if (!userAnswer.value.trim()) return
  store.submitAnswer(
    store.currentQuestion?.question || store.currentQuestion,
    userAnswer.value,
  )
  userAnswer.value = ''
}

function scoreGrade(score) {
  if (score >= 85) return 'grade-s'
  if (score >= 70) return 'grade-a'
  if (score >= 55) return 'grade-b'
  return 'grade-c'
}

function dimColor(score) {
  if (score >= 80) return '#059669'
  if (score >= 60) return '#eab308'
  return '#ef4444'
}
</script>

<style scoped>
.coach-page { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 800px; margin: 0 auto; }
.page-title { font-size: 1.8rem; color: #0f766e; margin-bottom: 1.5rem; }
.setup-card { background: #fff; border-radius: 12px; padding: 2rem; border: 1px solid #ccfbf1; }
.question-area { background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #ccfbf1; }
.progress-text { color: #0d9488; font-weight: 600; margin-bottom: 0.5rem; }
.question-card { background: #f0fdfa; border-radius: 10px; padding: 1.5rem; margin: 1.5rem 0; }
.question-card h3 { color: #0f766e; }
.context { color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; }
.feedback-area { background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #ccfbf1; }
.score-row { display: flex; align-items: center; gap: 1rem; margin: 1rem 0; }
.score-circle { width: 72px; height: 72px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 700; color: #fff; }
.score-circle.grade-s { background: #059669; }
.score-circle.grade-a { background: #0d9488; }
.score-circle.grade-b { background: #eab308; }
.score-circle.grade-c { background: #f97316; }
.dimensions { margin: 1rem 0; }
.dim-row { display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; }
.dim-label { width: 100px; font-size: 0.9rem; color: #555; }
.improved { background: #f0fdfa; padding: 1rem; border-radius: 8px; }
.feedback-actions { display: flex; gap: 0.75rem; margin-top: 1.5rem; justify-content: center; }
.finished-area { background: #fff; border-radius: 12px; padding: 2rem; border: 1px solid #ccfbf1; text-align: center; }
.summary-card { text-align: left; margin-top: 1.5rem; }
.summary-card h4 { color: #0f766e; margin: 1rem 0 0.5rem; }
</style>
