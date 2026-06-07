<template>
  <div class="coach-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">
        <el-icon style="margin-right:8px"><Microphone /></el-icon>
        AI 面试教练
      </h1>

      <!-- Phase transitions -->
      <Transition name="phase" mode="out-in">

        <!-- Setup -->
        <div v-if="store.phase === 'setup'" key="setup" class="setup-card card">
          <h2>开始模拟面试</h2>
          <el-form class="setup-form">
            <el-form-item label="面试类型">
              <el-select v-model="interviewType" style="width:200px" size="large">
                <el-option label="综合面" value="综合面" />
                <el-option label="技术面" value="技术面" />
                <el-option label="HR面" value="HR面" />
              </el-select>
            </el-form-item>
            <el-form-item label="难　　度">
              <el-select v-model="difficulty" style="width:200px" size="large">
                <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
            <el-form-item label="题目数量">
              <el-input-number v-model="questionCount" :min="3" :max="10" size="large" />
            </el-form-item>
            <el-button type="primary" size="large" @click="store.start(interviewType, difficulty, questionCount)" :loading="store.isLoading" class="start-btn">
              <el-icon style="margin-right:6px"><VideoPlay /></el-icon>
              开始面试
            </el-button>
          </el-form>
        </div>

        <!-- Answering -->
        <div v-else-if="store.phase === 'answering'" key="answering" class="question-area card">
          <div class="qa-progress">
            <span class="qa-progress-text">第 {{ store.currentIndex + 1 }} / {{ store.totalQuestions }} 题</span>
            <el-progress :percentage="Math.round((store.currentIndex + 1) / store.totalQuestions * 100)" :show-text="false" />
          </div>

          <div class="question-card-inner">
            <div class="question-label">题目</div>
            <h3>{{ store.currentQuestion?.question || store.currentQuestion }}</h3>
            <p v-if="store.currentQuestion?.context" class="context">{{ store.currentQuestion.context }}</p>
          </div>

          <el-input
            v-model="userAnswer"
            type="textarea"
            :rows="5"
            placeholder="请输入你的回答..."
            size="large"
            class="answer-input"
          />
          <el-button type="primary" size="large" @click="handleSubmit" :loading="store.isLoading" class="submit-btn">
            <el-icon style="margin-right:6px"><Finished /></el-icon>
            提交答案
          </el-button>
        </div>

        <!-- Feedback -->
        <div v-else-if="store.phase === 'feedback' && store.currentFeedback" key="feedback" class="feedback-area card">
          <h2>评分反馈</h2>

          <div class="score-section">
            <svg class="score-ring" width="90" height="90" viewBox="0 0 90 90">
              <circle cx="45" cy="45" r="39" fill="none" stroke="var(--green-100)" stroke-width="7"/>
              <circle
                cx="45" cy="45" r="39" fill="none"
                :stroke="scoreColor(store.currentFeedback.overall_score)"
                stroke-width="7" stroke-linecap="round"
                :stroke-dasharray="2 * Math.PI * 39"
                :stroke-dashoffset="2 * Math.PI * 39 * (1 - store.currentFeedback.overall_score / 100)"
                transform="rotate(-90 45 45)"
                class="score-ring-fill"
              />
              <text x="45" y="45" text-anchor="middle" dominant-baseline="central"
                :fill="scoreColor(store.currentFeedback.overall_score)"
                font-size="20" font-weight="800">{{ store.currentFeedback.overall_score }}</text>
            </svg>
            <span class="score-label-text">综合评分</span>
          </div>

          <div v-if="store.currentFeedback.dimensions" class="dimensions">
            <div v-for="(v, k) in store.currentFeedback.dimensions" :key="k" class="dim-row">
              <span class="dim-label">{{ k }}</span>
              <el-progress :percentage="v.score || v" :color="dimColor(v.score || v)" :stroke-width="10" />
            </div>
          </div>

          <div v-if="store.currentFeedback.strengths?.length" class="fb-section">
            <h4>
              <el-icon style="margin-right:4px; color: var(--green-600)"><CircleCheckFilled /></el-icon>
              优点
            </h4>
            <ul><li v-for="s in store.currentFeedback.strengths" :key="s">{{ s }}</li></ul>
          </div>

          <div v-if="store.currentFeedback.weaknesses?.length" class="fb-section">
            <h4>
              <el-icon style="margin-right:4px; color: #f59e0b"><WarningFilled /></el-icon>
              待改进
            </h4>
            <ul><li v-for="w in store.currentFeedback.weaknesses" :key="w">{{ w }}</li></ul>
          </div>

          <div v-if="store.currentFeedback.improved_answer" class="fb-section">
            <h4>
              <el-icon style="margin-right:4px; color: var(--green-600)"><Star /></el-icon>
              优化答案
            </h4>
            <p class="improved">{{ store.currentFeedback.improved_answer }}</p>
          </div>

          <div class="feedback-actions">
            <el-button v-if="store.currentIndex > 0" size="large" @click="store.prevQuestion()" class="nav-btn">
              <el-icon style="margin-right:4px"><ArrowLeft /></el-icon>
              上一题
            </el-button>
            <el-button type="primary" size="large" @click="store.nextQuestion()" class="nav-btn">
              {{ store.isLastQuestion ? '完成面试' : '下一题' }}
              <el-icon style="margin-left:4px"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- Finished -->
        <div v-else-if="store.phase === 'finished'" key="finished" class="finished-area card">
          <div class="finished-icon">
            <el-icon :size="48"><CircleCheckFilled /></el-icon>
          </div>
          <h2>面试结束</h2>
          <p class="finished-score">平均得分：<strong>{{ store.avgScore }} 分</strong></p>

          <div v-if="!store.summary">
            <el-button type="primary" size="large" @click="store.finishInterview()" :loading="store.isLoading">
              <el-icon style="margin-right:6px"><Cpu /></el-icon>
              AI 生成面试总结
            </el-button>
          </div>

          <div v-if="store.summary" class="summary-card">
            <div v-if="store.summary.overall_evaluation" class="fb-section">
              <h4>综合评价</h4>
              <p>{{ store.summary.overall_evaluation }}</p>
            </div>
            <div v-if="store.summary.strengths?.length" class="fb-section">
              <h4>优势</h4>
              <ul><li v-for="s in store.summary.strengths" :key="s">{{ s }}</li></ul>
            </div>
            <div v-if="store.summary.weaknesses?.length" class="fb-section">
              <h4>待改进</h4>
              <ul><li v-for="w in store.summary.weaknesses" :key="w">{{ w }}</li></ul>
            </div>
          </div>

          <el-button size="large" @click="store.restart()" style="margin-top:1.5rem" class="restart-btn">
            <el-icon style="margin-right:6px"><Refresh /></el-icon>
            重新开始
          </el-button>
        </div>

      </Transition>
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

function scoreColor(score) {
  if (score >= 85) return '#059669'
  if (score >= 70) return '#0d9488'
  if (score >= 55) return '#eab308'
  return '#f97316'
}

function dimColor(score) {
  if (score >= 80) return '#059669'
  if (score >= 60) return '#eab308'
  return '#ef4444'
}
</script>

<style scoped>
.coach-page { min-height: 100vh; background: var(--bg-page); }

.main-content {
  padding: 80px 1.5rem 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.8rem;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
}

/* ── Card ────────────────────────────────── */
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

/* ── Phase transition ────────────────────── */
.phase-enter-active,
.phase-leave-active {
  transition: opacity 0.2s var(--ease-out), transform 0.2s var(--ease-out);
}
.phase-enter-from { opacity: 0; transform: translateY(12px); }
.phase-leave-to { opacity: 0; transform: translateY(-12px); }

/* ── Setup ───────────────────────────────── */
.setup-card { padding: 2.5rem 2rem; }
.setup-card h2 {
  font-size: 1.3rem; color: var(--text-primary);
  margin: 0 0 1.5rem; font-weight: 700;
}
.setup-form :deep(.el-form-item__label) {
  font-weight: 600; color: var(--text-secondary);
}
.start-btn {
  font-weight: 700; padding: 12px 36px;
  border-radius: var(--radius-md);
}

/* ── Answering ───────────────────────────── */
.question-area { padding: 2rem; }
.qa-progress { margin-bottom: 1.5rem; }
.qa-progress-text {
  color: var(--green-600); font-weight: 600;
  margin-bottom: 0.5rem; display: block;
}
.question-card-inner {
  background: var(--green-50);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid var(--green-500);
}
.question-label {
  font-size: 0.75rem; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--green-600);
  font-weight: 700; margin-bottom: 0.5rem;
}
.question-card-inner h3 {
  color: var(--text-primary); font-size: 1.15rem;
  line-height: 1.5; margin: 0;
}
.context {
  color: var(--text-secondary); font-size: 0.9rem;
  margin-top: 0.75rem; line-height: 1.5;
}
.answer-input { margin-bottom: 1rem; }
.submit-btn {
  font-weight: 700; padding: 12px 28px;
  border-radius: var(--radius-md);
}

/* ── Feedback ────────────────────────────── */
.feedback-area { padding: 2rem; }
.feedback-area h2 {
  font-size: 1.3rem; color: var(--text-primary);
  margin: 0 0 1.25rem; font-weight: 700;
}
.score-section {
  display: flex; align-items: center; gap: 1.25rem;
  margin-bottom: 1.5rem;
}
.score-ring-fill {
  transition: stroke-dashoffset 1s var(--ease-out);
}
.score-label-text {
  font-weight: 600; color: var(--text-secondary); font-size: 1.05rem;
}
.dimensions { margin: 1rem 0; }
.dim-row { display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; }
.dim-label { width: 100px; font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; }
.fb-section { margin-top: 1rem; }
.fb-section h4 {
  color: var(--text-primary); margin: 0 0 0.5rem;
  font-size: 0.95rem; display: flex; align-items: center;
}
.fb-section ul { padding-left: 1.25rem; margin: 0; }
.fb-section li { margin: 0.3rem 0; color: var(--text-secondary); font-size: 0.9rem; }
.fb-section p { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; }
.improved {
  background: var(--green-50); padding: 1rem;
  border-radius: var(--radius-md); color: var(--text-primary);
}
.feedback-actions {
  display: flex; gap: 0.75rem; margin-top: 1.5rem;
  justify-content: center;
}
.nav-btn { font-weight: 600; }

/* ── Finished ────────────────────────────── */
.finished-area { padding: 3rem 2rem; text-align: center; }
.finished-icon { color: var(--green-500); margin-bottom: 1rem; }
.finished-area h2 {
  font-size: 1.5rem; color: var(--text-primary);
  margin: 0 0 0.5rem; font-weight: 700;
}
.finished-score {
  color: var(--text-secondary); font-size: 1.05rem; margin-bottom: 1.5rem;
}
.finished-score strong {
  color: var(--green-600); font-size: 1.3rem; font-weight: 800;
}
.summary-card { text-align: left; margin-top: 1.5rem; }
.summary-card .fb-section { margin-top: 1.25rem; }
.restart-btn {
  border-radius: var(--radius-md); font-weight: 600;
  padding: 12px 28px;
}

@media (max-width: 768px) {
  .main-content { padding: 70px 1rem 1.5rem; }
  .page-title { font-size: 1.4rem; }

  .setup-card, .question-area, .feedback-area, .finished-area {
    padding: 1.5rem 1rem;
  }

  .setup-form :deep(.el-form-item) {
    flex-direction: column;
    align-items: stretch;
  }
  .setup-form :deep(.el-form-item__label) {
    margin-bottom: 0.25rem;
  }
  .setup-form :deep(.el-select) { width: 100% !important; }

  .start-btn, .submit-btn, .nav-btn, .restart-btn {
    width: 100%;
    justify-content: center;
  }

  .feedback-actions { flex-direction: column; }
  .feedback-actions .nav-btn { width: 100%; justify-content: center; }

  .dim-row { flex-direction: column; gap: 0.25rem; align-items: stretch; }
  .dim-label { width: auto; }

  .score-section { justify-content: center; }

  .question-card-inner { padding: 1rem; }
  .question-card-inner h3 { font-size: 1rem; }
}
</style>
