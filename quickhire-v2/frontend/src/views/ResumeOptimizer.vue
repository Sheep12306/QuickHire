<template>
  <div class="optimizer-page">
    <NavBar />
    <main class="main-content">
      <el-alert v-if="!auth.isLoggedIn" type="info" :closable="false" show-icon class="login-banner">
        当前为体验模式，登录后可保存优化历史记录。
        <el-button text type="primary" @click="$router.push('/login')">立即登录</el-button>
      </el-alert>

      <!-- Resume Input Section -->
      <div class="input-section card">
        <el-input
          v-model="store.resumeText"
          type="textarea"
          :rows="8"
          placeholder="在此粘贴您的简历内容，或拖拽文件到下方上传区域..."
          size="large"
        />
        <div class="input-actions">
          <el-upload
            drag
            :auto-upload="false"
            :show-file-list="false"
            @change="handleFileUpload"
            accept=".txt,.md,.docx,.pdf"
            class="upload-compact"
          >
            <div class="upload-inline">
              <el-icon><UploadFilled /></el-icon>
              <span>拖拽或点击上传</span>
            </div>
          </el-upload>
          <el-button @click="loadDemo">
            <el-icon style="margin-right:4px"><Document /></el-icon>
            加载示例
          </el-button>
          <el-input
            v-model="store.targetPosition"
            placeholder="* 目标岗位（必填，如：Python开发工程师）"
            class="position-input"
            clearable
            :class="{ 'is-required': !store.targetPosition }"
          />
        </div>
      </div>

      <!-- Step Indicator -->
      <div class="step-progress">
        <div class="step-progress-track"></div>
        <div class="step-progress-items">
          <div class="step-node" :class="{ active: store.hasInput, done: store.hasOptimized }">
            <div class="step-node-circle">
              <el-icon v-if="store.hasOptimized"><Check /></el-icon>
              <span v-else>1</span>
            </div>
            <span class="step-node-label">输入简历</span>
          </div>
          <div class="step-node" :class="{ active: store.hasOptimized, done: store.hasAnalysis }">
            <div class="step-node-circle">
              <el-icon v-if="store.hasAnalysis"><Check /></el-icon>
              <span v-else>2</span>
            </div>
            <span class="step-node-label">AI 优化</span>
          </div>
          <div class="step-node" :class="{ active: store.hasQuestions }">
            <div class="step-node-circle">
              <span>3</span>
            </div>
            <span class="step-node-label">面试题</span>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        <!-- Tab 1: Optimize -->
        <el-tab-pane name="optimize">
          <template #label>
            <span class="tab-label">
              <el-icon><EditPen /></el-icon> 简历优化
            </span>
          </template>

          <div class="config-bar">
            <span class="config-label">优化风格：</span>
            <el-select v-model="store.optimizationStyle" class="style-select">
              <el-option v-for="s in styles" :key="s" :label="s" :value="s" />
            </el-select>
            <el-button type="primary" @click="handleOptimize" :loading="store.isOptimizing" :disabled="!store.hasInput || (!usage.unlimited && usage.optimizeRemaining <= 0)">
              <el-icon style="margin-right:4px"><MagicStick /></el-icon>
              开始优化
            </el-button>
            <el-tag v-if="auth.isLoggedIn && !usage.unlimited" type="warning" effect="plain" size="small">
              今日剩余 {{ usage.optimizeRemaining }} 次
            </el-tag>
            <el-tag v-else-if="auth.isLoggedIn && usage.unlimited" type="success" effect="plain" size="small">
              无限制
            </el-tag>
            <el-button @click="store.clearOptimized()" v-if="store.hasOptimized">清空结果</el-button>
          </div>

          <div v-if="store.hasOptimized" class="result-card card">
            <div class="analysis-section">
              <div class="analysis-header" @click="showAnalysis = !showAnalysis">
                <span>
                  <el-icon style="margin-right:6px"><DataAnalysis /></el-icon>
                  优化分析与建议
                </span>
                <span class="toggle-icon">{{ showAnalysis ? '收起 ▲' : '展开 ▼' }}</span>
              </div>
              <div v-show="showAnalysis">
                <div class="highlight-box comparison-box">
                  <div class="box-header">
                    <span>
                      <el-icon style="margin-right:4px"><Switch /></el-icon>
                      优化对比 — 改了哪些地方
                    </span>
                    <el-button text size="small" @click.stop="copyText(store.optimizedResult.comparison)">复制</el-button>
                  </div>
                  <pre>{{ store.optimizedResult?.comparison || '（AI 未返回优化对比，可尝试重新优化）' }}</pre>
                </div>
                <div class="highlight-box hr-box">
                  <div class="box-header">
                    <span>
                      <el-icon style="margin-right:4px"><UserFilled /></el-icon>
                      HR 视角点评 — 投递与面试策略
                    </span>
                    <el-button text size="small" @click.stop="copyText(store.optimizedResult.hr_review)">复制</el-button>
                  </div>
                  <pre>{{ store.optimizedResult?.hr_review || '（AI 未返回 HR 点评，可尝试重新优化）' }}</pre>
                </div>
              </div>
            </div>

            <div class="resume-output">
              <div class="resume-output-header">
                <span>
                  <el-icon style="margin-right:4px"><Star /></el-icon>
                  优化后简历（可复制/导出投递）
                </span>
                <div class="resume-output-actions">
                  <el-button type="primary" @click="copyText(store.optimizedResult.optimized_text)">
                    <el-icon style="margin-right:4px"><CopyDocument /></el-icon>
                    复制简历
                  </el-button>
                  <el-button type="success" @click="handleExportClick">
                    <el-icon style="margin-right:4px"><Printer /></el-icon>
                    导出 PDF
                  </el-button>
                </div>
              </div>
              <div class="optimized-text">
                <pre>{{ store.optimizedResult.optimized_text }}</pre>
              </div>
            </div>
          </div>

          <el-empty v-if="!store.hasOptimized && !store.isOptimizing" description="输入简历和目标岗位，点击「开始优化」" />
        </el-tab-pane>

        <!-- Tab 2: AI Deep Analysis -->
        <el-tab-pane name="analyze">
          <template #label>
            <span class="tab-label">
              <el-icon><Search /></el-icon> AI 深度分析
            </span>
          </template>

          <div class="config-bar">
            <el-button @click="store.scan()" :disabled="!store.hasInput">
              <el-icon style="margin-right:4px"><Lightning /></el-icon>
              快速扫描（本地算法）
            </el-button>
            <el-button type="primary" @click="handleAnalyze" :loading="store.isAnalyzing" :disabled="!store.hasInput || (!usage.unlimited && usage.diagnoseRemaining <= 0)">
              <el-icon style="margin-right:4px"><Cpu /></el-icon>
              AI 深度分析
            </el-button>
            <el-tag v-if="auth.isLoggedIn && !usage.unlimited" type="warning" effect="plain" size="small">
              今日剩余 {{ usage.diagnoseRemaining }} 次
            </el-tag>
            <el-tag v-else-if="auth.isLoggedIn && usage.unlimited" type="success" effect="plain" size="small">
              无限制
            </el-tag>
            <el-button @click="store.clearAnalysis()" v-if="store.hasAnalysis">清空结果</el-button>
          </div>

          <div v-if="store.hasAnalysis" class="result-card card">
            <div v-if="store.analysisResult.overall_score" class="score-section">
              <svg class="score-ring" width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" fill="none" stroke="var(--green-100)" stroke-width="8"/>
                <circle
                  cx="50" cy="50" r="44" fill="none"
                  :stroke="scoreColor(store.analysisResult.overall_score)"
                  stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="2 * Math.PI * 44"
                  :stroke-dashoffset="2 * Math.PI * 44 * (1 - store.analysisResult.overall_score / 100)"
                  transform="rotate(-90 50 50)"
                  class="score-ring-fill"
                />
                <text x="50" y="50" text-anchor="middle" dominant-baseline="central"
                  :fill="scoreColor(store.analysisResult.overall_score)"
                  font-size="22" font-weight="800">{{ store.analysisResult.overall_score }}</text>
              </svg>
              <span class="score-label-text">综合评分</span>
            </div>

            <div v-if="store.analysisResult.defects?.length" class="section-block">
              <h3>
                <el-icon style="margin-right:4px"><WarningFilled /></el-icon>
                发现的问题 ({{ store.analysisResult.defects.length }})
              </h3>
              <div v-for="(d, i) in store.analysisResult.defects" :key="i" class="defect-item">
                <el-tag :type="d.severity === 'high' ? 'danger' : d.severity === 'medium' ? 'warning' : 'info'" size="small">
                  {{ d.severity === 'high' ? '严重' : d.severity === 'medium' ? '中等' : '轻微' }}
                </el-tag>
                <span>{{ d.description }}</span>
              </div>
            </div>

            <div v-if="store.analysisResult.suggestions?.length" class="section-block">
              <h3>
                <el-icon style="margin-right:4px"><Sunny /></el-icon>
                优化建议
              </h3>
              <ul class="suggestion-list">
                <li v-for="(s, i) in store.analysisResult.suggestions" :key="i">{{ s }}</li>
              </ul>
            </div>

            <div v-if="diagnosisHasContent" class="section-block">
              <h3>
                <el-icon style="margin-right:4px"><Cpu /></el-icon>
                AI 多维诊断
              </h3>

              <div v-if="dimensionScores.length" class="dimension-grid">
                <div v-for="d in dimensionScores" :key="d.key" class="dim-card">
                  <div class="dim-name">{{ d.label }}</div>
                  <el-progress :percentage="d.value" :color="dimColor(d.value)" :stroke-width="10" />
                  <div class="dim-score">{{ d.value }}分</div>
                </div>
              </div>

              <div v-if="diagnosisData?.diagnosis?.keyword_match" class="section-block">
                <h4>
                  <el-icon style="margin-right:4px"><Aim /></el-icon>
                  关键词匹配
                </h4>
                <div class="keyword-row">
                  <span v-for="k in diagnosisData.diagnosis.keyword_match.matched" :key="k" class="kw-tag kw-matched">{{ k }}</span>
                  <span v-for="k in diagnosisData.diagnosis.keyword_match.missing" :key="k" class="kw-tag kw-missing">{{ k }}</span>
                </div>
              </div>

              <div v-if="diagnosisData?.weaknesses?.length" class="section-block">
                <h4>
                  <el-icon style="margin-right:4px"><Warning /></el-icon>
                  薄弱环节
                </h4>
                <div v-for="(w, i) in diagnosisData.weaknesses" :key="i" class="weak-item">
                  <strong>{{ w.area || w }}</strong>
                  <p>{{ w.description || '' }}</p>
                  <p v-if="w.suggestion" class="suggestion-text">{{ w.suggestion }}</p>
                </div>
              </div>
            </div>
          </div>

          <el-empty v-if="!store.hasAnalysis && !store.isAnalyzing" description="点击「AI深度分析」或「快速扫描」" />
        </el-tab-pane>

        <!-- Tab 3: Interview Questions -->
        <el-tab-pane name="questions">
          <template #label>
            <span class="tab-label">
              <el-icon><Collection /></el-icon> 面试题生成
            </span>
          </template>

          <div class="config-bar">
            <el-input v-model="store.targetPosition" placeholder="* 目标岗位" class="position-input-small" />
            <el-select v-model="qDifficulty" class="difficulty-select">
              <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
            </el-select>
            <el-select v-model="qTypes" multiple class="types-select" placeholder="题目类型">
              <el-option v-for="t in questionTypes" :key="t" :label="t" :value="t" />
            </el-select>
            <span class="config-label">数量：</span>
            <el-input-number v-model="qCount" :min="3" :max="15" />
            <el-button type="primary" @click="handleGenQuestions" :loading="store.isGenerating">
              <el-icon style="margin-right:4px"><MagicStick /></el-icon>
              生成面试题
            </el-button>
            <el-button @click="store.clearQuestions()" v-if="store.hasQuestions">清空</el-button>
            <el-button v-if="store.hasQuestions" type="success" @click="handleSaveQuestions" :loading="savingQuestions">
              <el-icon style="margin-right:4px"><FolderAdd /></el-icon>
              存入题库
            </el-button>
          </div>

          <div v-if="store.hasQuestions" class="question-list">
            <div v-for="(q, i) in store.questions" :key="i" class="q-card card">
              <div class="q-header">
                <span class="q-number">#{{ i + 1 }}</span>
                <el-tag v-if="q.type" size="small" effect="plain">{{ q.type }}</el-tag>
                <el-tag v-if="q.difficulty" size="small" effect="plain" style="margin-left:4px">{{ q.difficulty }}</el-tag>
                <span class="q-text">{{ q.question || q }}</span>
                <el-button
                  :type="q._fav ? 'warning' : 'default'" size="small" circle
                  @click="q._fav = !q._fav; handleFavQuestion(q, i)"
                >
                  <el-icon><StarFilled v-if="q._fav" /><Star v-else /></el-icon>
                </el-button>
              </div>
              <el-button text type="primary" size="small" @click="q._show = !q._show">
                {{ q._show ? '隐藏答案 ▲' : '查看答案 ▼' }}
              </el-button>
              <div v-if="q._show" class="q-detail-box">
                <div v-if="q.answer"><strong>答案：</strong>{{ q.answer }}</div>
                <div v-if="q.answer_guide"><strong>思路：</strong>{{ q.answer_guide }}</div>
                <div v-if="q.answer_script"><strong>话术：</strong>{{ q.answer_script }}</div>
              </div>
            </div>
            <el-button type="primary" @click="copyQuestions" style="margin-top:1rem">
              <el-icon style="margin-right:4px"><CopyDocument /></el-icon>
              复制全部题目
            </el-button>
          </div>

          <el-empty v-if="!store.hasQuestions && !store.isGenerating" description="输入目标岗位，配置参数后点击「生成面试题」" />
        </el-tab-pane>
      </el-tabs>

      <!-- PDF Export Dialog -->
      <TemplatePicker
        v-model="showExportDialog"
        :resume-text="store.optimizedResult?.optimized_text || ''"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'
import NavBar from '../components/layout/NavBar.vue'
import TemplatePicker from '../components/resume/TemplatePicker.vue'
import { generatePracticeQuestions, savePracticeQuestions, toggleFavorite } from '../api/practice'
import api from '../api'

const auth = useAuthStore()
const store = useResumeStore()
const activeTab = ref('optimize')
const showAnalysis = ref(true)

const styles = ['简洁专业', '突出业绩', '技术导向', '创新风格']
const difficulties = ['入门', '基础', '中等', '面试高频', '深度深挖']
const questionTypes = ['选择题', '简答题', '项目手撕题', '场景面试题', '压力面试题']

const qDifficulty = ref('中等')
const qTypes = ref(['简答题', '项目手撕题'])
const qCount = ref(5)
const savingQuestions = ref(false)
const showExportDialog = ref(false)

const usage = reactive({ unlimited: false, optimizeRemaining: 0, diagnoseRemaining: 0, dailyLimit: 2 })

async function loadUsage() {
  if (!auth.isLoggedIn) return
  try {
    const { data } = await api.get('/profile/usage')
    Object.assign(usage, data)
  } catch { /* */ }
}

onMounted(() => loadUsage())

function handleExportClick() {
  ElMessage.warning('PDF 导出功能正在维护中，敬请期待')
}

const diagnosisData = computed(() => {
  const ar = store.analysisResult
  if (!ar || ar.defects) return null
  return ar.diagnosis ? ar : null
})

const diagnosisHasContent = computed(() => {
  return diagnosisData.value?.diagnosis || diagnosisData.value?.weaknesses?.length
})

const dimensionScores = computed(() => {
  const diag = diagnosisData.value?.diagnosis
  if (!diag) return []
  const dimNameMap = {
    completeness: '完整度', keyword_match: '关键词匹配',
    quantification: '量化成果', structure: '结构逻辑', language: '语言表达',
    competitiveness: '竞争力', accuracy: '准确性', depth: '深度',
    expression: '表达力', highlights: '亮点',
  }
  const results = []
  Object.entries(diag).forEach(([key, val]) => {
    if (typeof val === 'object' && val !== null && 'score' in val) {
      results.push({ key, label: dimNameMap[key] || key, value: val.score })
    } else if (typeof val === 'number') {
      results.push({ key, label: dimNameMap[key] || key, value: val })
    }
  })
  return results
})

function scoreColor(score) {
  if (score >= 85) return '#059669'
  if (score >= 70) return '#0d9488'
  if (score >= 55) return '#eab308'
  if (score >= 40) return '#f97316'
  return '#ef4444'
}

function dimColor(score) {
  if (score >= 80) return '#059669'
  if (score >= 60) return '#eab308'
  return '#ef4444'
}

async function handleFileUpload(file) {
  try {
    await store.upload(file.raw)
    ElMessage.success(`已解析：${file.name}`)
  } catch {
    ElMessage.error('文件解析失败，请检查文件格式')
  }
}

function loadDemo() {
  store.resumeText = `张三 | 男 | 1997年 | 3年工作经验
邮箱：zhangsan@example.com | 手机：13800138000
期望职位：Python后端开发工程师

教育经历：
2015-2019 清华大学 计算机科学与技术 本科

工作经历：
2020-至今 某科技有限公司 | Python开发工程师
- 负责公司核心业务系统后端开发，使用Django+MySQL架构
- 优化数据库查询性能，将核心API响应时间从500ms降至80ms
- 参与微服务架构改造，拆分单体应用为12个微服务
- 编写自动化测试用例200+，测试覆盖率达85%

项目经验：
2022年 智能客服系统 | 核心开发者
- 使用FastAPI+WebSocket实现实时消息推送
- 集成NLP模型实现智能问答，准确率92%
- 系统支撑日均10万+次对话请求`
  store.targetPosition = 'Python后端开发工程师'
  ElMessage.success('已加载示例简历')
}

async function handleOptimize() {
  if (!store.targetPosition.trim()) {
    ElMessage.error('请填写目标岗位')
    return
  }
  await store.optimize()
  loadUsage()
}

async function handleAnalyze() {
  await store.analyze()
  loadUsage()
}

async function handleGenQuestions() {
  if (!store.targetPosition.trim()) {
    ElMessage.error('请填写目标岗位')
    return
  }
  store.isGenerating = true
  try {
    const { data } = await generatePracticeQuestions({
      target_position: store.targetPosition.trim(),
      difficulty: qDifficulty.value,
      question_types: qTypes.value,
      question_count: qCount.value,
    })
    store.questions = (data.questions || []).map(q => ({ ...q, _show: false, _fav: false }))
  } catch {
    ElMessage.error('生成失败，请检查 API 配置')
  } finally {
    store.isGenerating = false
  }
}

async function handleSaveQuestions() {
  savingQuestions.value = true
  try {
    await savePracticeQuestions({
      position: store.targetPosition.trim(),
      questions: store.questions,
    })
    ElMessage.success('已存入题库，可在「面试刷题」中查看')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingQuestions.value = false
  }
}

async function handleFavQuestion(q, idx) {
  try {
    if (q.id) await toggleFavorite(q.id)
  } catch { /* non-critical */ }
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制到剪贴板'))
}

function copyQuestions() {
  const text = store.questions.map((q, i) =>
    `#${i + 1} ${q.question || q}\n  类型：${q.type || ''} | 难度：${q.difficulty || ''}\n  答案：${q.answer || ''}\n  思路：${q.answer_guide || ''}\n  话术：${q.answer_script || ''}`
  ).join('\n\n')
  copyText(text)
}
</script>

<style scoped>
.optimizer-page { min-height: 100vh; background: var(--bg-page); }

.main-content { padding: 80px 1.5rem 2rem; max-width: 1100px; margin: 0 auto; }

.login-banner { margin-bottom: 1rem; border-radius: var(--radius-md); }

/* ── Card ────────────────────────────────── */
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

/* ── Input section ───────────────────────── */
.input-section { padding: 1.5rem; margin-bottom: 1.5rem; }
.input-actions {
  display: flex; gap: 0.75rem; margin-top: 1rem;
  align-items: center; flex-wrap: wrap;
}
.upload-compact { width: auto; }
.upload-compact :deep(.el-upload) { display: inline-block; }
.upload-compact :deep(.el-upload-dragger) {
  padding: 0.5rem 1.25rem; width: auto; height: auto;
}
.upload-inline {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.85rem; color: var(--text-secondary); white-space: nowrap;
}
.is-required :deep(.el-input__inner) { border-color: #f56c6c; }

/* ── Step progress ───────────────────────── */
.step-progress {
  position: relative;
  margin: 0 0 1.5rem;
  padding: 0.5rem 1rem;
}
.step-progress-items {
  display: flex;
  justify-content: center;
  gap: 3rem;
  position: relative;
  z-index: 1;
}
.step-progress-track {
  position: absolute;
  top: 22px;
  left: calc(50% - 140px);
  right: calc(50% - 140px);
  height: 2px;
  background: var(--border-default);
  border-radius: 2px;
}
.step-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.step-node-circle {
  width: 44px; height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface);
  border: 2px solid var(--border-default);
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.85rem;
  transition: all var(--duration-normal) var(--ease-out);
}
.step-node.active .step-node-circle {
  border-color: var(--green-500);
  color: var(--green-600);
  background: var(--green-50);
}
.step-node.done .step-node-circle {
  border-color: var(--green-600);
  background: var(--green-600);
  color: #fff;
}
.step-node-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
}
.step-node.active .step-node-label { color: var(--green-600); font-weight: 600; }
.step-node.done .step-node-label { color: var(--green-600); }

/* ── Tabs ────────────────────────────────── */
.main-tabs :deep(.el-tabs__content) {
  padding: 1.25rem;
}
.tab-label {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ── Config bar ──────────────────────────── */
.config-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: var(--bg-subtle);
  border-radius: var(--radius-md);
}
.config-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* ── Result card ─────────────────────────── */
.result-card { margin-top: 1rem; overflow: hidden; }

.analysis-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.5rem;
  background: var(--bg-subtle);
  cursor: pointer; font-weight: 600;
  color: var(--text-secondary); font-size: 0.95rem; user-select: none;
}
.analysis-header:hover { background: var(--bg-hover); }
.toggle-icon { font-size: 0.75rem; color: var(--text-muted); }

.highlight-box { padding: 1rem 1.5rem; }
.highlight-box pre {
  white-space: pre-wrap; font-size: 0.88rem;
  line-height: 1.65; margin: 0;
}
.box-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem;
}

.comparison-box {
  background: var(--green-50);
  border-bottom: 1px solid var(--green-100);
}
.comparison-box .box-header { color: var(--green-800); }
.comparison-box pre { color: var(--green-900); }

.hr-box {
  background: #eff6ff;
  border-bottom: 1px solid #dbeafe;
}
.hr-box .box-header { color: #1e40af; }
.hr-box pre { color: #1e3a5f; }

.resume-output { padding: 1.5rem; }
.resume-output-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem; font-weight: 700;
  color: var(--green-700); font-size: 1.05rem;
}
.resume-output-actions { display: flex; gap: 0.5rem; }

.optimized-text {
  background: var(--bg-subtle);
  border: 1px solid var(--green-100);
  border-radius: var(--radius-md);
}
.optimized-text pre {
  white-space: pre-wrap; padding: 1.25rem;
  font-size: 0.9rem; line-height: 1.7;
  color: var(--text-primary); margin: 0; min-height: 200px;
}

/* ── Score ───────────────────────────────── */
.score-section {
  display: flex; align-items: center; gap: 1.5rem;
  padding: 1.5rem; justify-content: center;
}
.score-ring-fill {
  transition: stroke-dashoffset 1.2s var(--ease-out);
}
.score-label-text {
  font-weight: 600; color: var(--text-secondary); font-size: 1.1rem;
}

/* ── Section blocks ──────────────────────── */
.section-block { padding: 0 1.5rem 1rem; }
.section-block h3 {
  color: var(--text-primary); font-size: 0.95rem;
  margin-bottom: 0.75rem; display: flex; align-items: center;
}
.section-block h4 {
  color: var(--text-primary); font-size: 0.88rem;
  margin-bottom: 0.5rem; display: flex; align-items: center;
}
.defect-item {
  display: flex; gap: 0.5rem; align-items: center;
  padding: 0.3rem 0; color: var(--text-secondary);
}
.suggestion-list { padding-left: 1.2rem; }
.suggestion-list li { margin: 0.3rem 0; color: var(--text-secondary); }
.dimension-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 0.5rem; }
.dim-card { background: var(--bg-subtle); border-radius: var(--radius-md); padding: 1rem; text-align: center; }
.dim-name { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 600; }
.dim-score { font-size: 0.8rem; color: var(--green-600); margin-top: 0.3rem; font-weight: 600; }
.keyword-row { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.kw-tag { padding: 3px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; }
.kw-matched { background: var(--green-100); color: var(--green-800); }
.kw-missing { background: #fee2e2; color: #991b1b; text-decoration: line-through; }
.weak-item { padding: 0.5rem 0; border-bottom: 1px solid var(--border-light); }
.weak-item p { margin: 0.25rem 0; font-size: 0.9rem; color: var(--text-secondary); }
.suggestion-text { color: var(--green-600) !important; font-weight: 500; }

/* ── Question cards ──────────────────────── */
.question-list { margin-top: 1rem; }
.q-card { padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.q-header {
  font-weight: 600; color: var(--green-700);
  margin-bottom: 0.5rem; display: flex;
  align-items: center; flex-wrap: wrap; gap: 0.3rem;
}
.q-number {
  background: var(--green-600); color: #fff;
  border-radius: 6px; padding: 2px 8px;
  font-size: 0.78rem; flex-shrink: 0; font-weight: 700;
}
.q-text { flex: 1; min-width: 200px; margin-left: 0.5rem; font-size: 0.95rem; }
.q-detail-box {
  margin-top: 0.75rem; padding: 0.85rem;
  background: var(--bg-subtle); border-radius: var(--radius-md);
  font-size: 0.9rem; color: var(--text-secondary);
  line-height: 1.6;
}
.q-detail-box div { margin-top: 0.35rem; }

/* ── Responsive input widths ──────────────── */
.position-input { width: 260px; }
.position-input-small { width: 200px; }
.style-select { width: 160px; }
.difficulty-select { width: 120px; }
.types-select { width: 260px; }

/* ── Mobile ───────────────────────────────── */
@media (max-width: 768px) {
  .main-content { padding: 70px 1rem 1.5rem; }

  /* Input section */
  .input-section { padding: 1rem; }
  .input-actions { flex-direction: column; }
  .input-actions > * { width: 100%; }
  .position-input { width: 100%; }
  .upload-compact :deep(.el-upload-dragger) { width: 100%; }

  /* Step progress - hide track, stack items */
  .step-progress-track { display: none; }
  .step-progress-items { gap: 1rem; flex-wrap: wrap; }
  .step-node { flex: 1; min-width: 80px; }

  /* Config bar */
  .config-bar { flex-direction: column; align-items: stretch; }
  .config-bar > * { width: 100%; }
  .style-select, .position-input-small, .difficulty-select, .types-select { width: 100%; }

  /* Result cards */
  .resume-output-header { flex-direction: column; gap: 0.75rem; align-items: flex-start; }
  .resume-output-actions { flex-direction: column; width: 100%; }
  .resume-output-actions .el-button { width: 100%; }

  .analysis-header { flex-direction: column; gap: 0.5rem; align-items: flex-start; padding: 0.75rem 1rem; }
  .highlight-box { padding: 0.75rem 1rem; }
  .highlight-box pre { font-size: 0.82rem; }

  /* Score section */
  .score-section { flex-direction: column; gap: 0.5rem; text-align: center; }

  /* Dimension grid */
  .dimension-grid { grid-template-columns: 1fr; }

  /* Question cards */
  .q-card { padding: 0.75rem 1rem; }
  .q-header { flex-direction: column; align-items: flex-start; }
  .q-text { margin-left: 0; margin-top: 0.25rem; font-size: 0.88rem; }
  .q-detail-box { font-size: 0.85rem; }

  /* Resume output */
  .resume-output { padding: 1rem; }
  .optimized-text pre { padding: 0.75rem; font-size: 0.82rem; }

  /* Section blocks */
  .section-block { padding: 0 1rem 0.75rem; }
  .section-block h3 { font-size: 0.9rem; }
}

@media (max-width: 480px) {
  .step-progress-items { gap: 0.5rem; }
  .step-node-label { font-size: 0.7rem; }
  .step-node-circle { width: 36px; height: 36px; font-size: 0.75rem; }
}
</style>
