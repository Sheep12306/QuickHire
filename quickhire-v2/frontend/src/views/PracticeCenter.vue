<template>
  <div class="practice-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">
        <el-icon style="margin-right:8px"><Notebook /></el-icon>
        面试刷题中心
      </h1>

      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        <!-- Tab 1: AI Generate -->
        <el-tab-pane name="generate">
          <template #label>
            <span class="tab-label">
              <el-icon><MagicStick /></el-icon> AI 出题
            </span>
          </template>

          <div class="gen-card card">
            <el-form inline>
              <el-form-item label="目标岗位" required>
                <el-input v-model="genPosition" placeholder="如：Python后端开发" style="width:240px" />
              </el-form-item>
              <el-form-item label="难度">
                <el-select v-model="genDifficulty" style="width:120px">
                  <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
                </el-select>
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="genTypes" multiple style="width:240px">
                  <el-option v-for="t in questionTypes" :key="t" :label="t" :value="t" />
                </el-select>
              </el-form-item>
              <el-form-item label="数量">
                <el-input-number v-model="genCount" :min="3" :max="15" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleGenerate" :loading="generating">
                  <el-icon style="margin-right:4px"><MagicStick /></el-icon>
                  AI 生成
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-if="generatedQuestions.length" class="q-section">
            <div class="section-head">
              <span>已生成 {{ generatedQuestions.length }} 道「{{ genPosition }}」面试题</span>
              <el-button type="success" @click="handleSaveAll" :loading="saving">
                <el-icon style="margin-right:4px"><FolderAdd /></el-icon>
                全部存入题库
              </el-button>
            </div>
            <q-card v-for="(q, i) in generatedQuestions" :key="'g'+i" :q="q" :idx="i+1" :show-fav="auth.isLoggedIn && !!q.id" @fav="handleFavorite(q)" />
          </div>
        </el-tab-pane>

        <!-- Tab 2: Browse -->
        <el-tab-pane name="browse">
          <template #label>
            <span class="tab-label">
              <el-icon><Collection /></el-icon> 题库浏览
            </span>
          </template>

          <div class="filter-bar card">
            <el-input v-model="filterPosition" placeholder="搜索岗位" style="width:200px" clearable @clear="loadBrowse" @keyup.enter="loadBrowse" />
            <el-select v-model="filterDifficulty" placeholder="难度" clearable style="width:120px" @change="loadBrowse">
              <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
            </el-select>
            <el-select v-model="filterType" placeholder="类型" clearable style="width:120px" @change="loadBrowse">
              <el-option v-for="t in questionTypes" :key="t" :label="t" :value="t" />
            </el-select>
            <el-button type="primary" @click="loadBrowse">搜索</el-button>
          </div>

          <div v-if="browseList.length" class="q-section">
            <div class="section-head">共 {{ browseTotal }} 道题目</div>
            <q-card v-for="(q, i) in browseList" :key="q.id" :q="q" :idx="(browsePage-1)*20 + i + 1" :show-fav="true" @fav="handleFavorite(q)" />

            <el-pagination
              v-if="browseTotal > 20"
              :current-page="browsePage" :page-size="20" :total="browseTotal"
              layout="prev, pager, next" @current-change="(p) => { browsePage = p; loadBrowse() }"
              style="margin-top:1rem; justify-content:center"
            />
          </div>
          <el-empty v-else description="题库中暂无题目，先生成并保存一些吧" />
        </el-tab-pane>

        <!-- Tab 3: Favorites -->
        <el-tab-pane name="favorites" v-if="auth.isLoggedIn">
          <template #label>
            <span class="tab-label">
              <el-icon><StarFilled /></el-icon> 我的收藏
            </span>
          </template>

          <div v-if="favList.length" class="q-section">
            <div class="section-head">已收藏 {{ favList.length }} 道题目</div>
            <q-card v-for="(q, i) in favList" :key="'f'+q.id" :q="q" :idx="i+1" :show-fav="true" :is-fav="true" @fav="handleFavorite(q)" />
          </div>
          <el-empty v-else description="还没有收藏任何题目" />
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script>
export default {
  components: {
    QCard: {
      props: ['q', 'idx', 'showFav', 'isFav'],
      emits: ['fav'],
      template: `
        <div class="q-card card">
          <div class="q-top">
            <span class="q-idx">#{{ idx }}</span>
            <el-tag v-if="q.type" size="small" effect="plain">{{ q.type }}</el-tag>
            <el-tag v-if="q.difficulty" size="small" effect="plain" style="margin-left:4px">{{ q.difficulty }}</el-tag>
            <el-tag v-if="q.position" size="small" effect="plain" type="info" style="margin-left:4px">{{ q.position }}</el-tag>
            <span class="q-text">{{ q.question }}</span>
            <el-button
              v-if="showFav"
              :type="isFav || q.favorited ? 'warning' : 'default'"
              size="small" circle
              @click="$emit('fav')"
              style="flex-shrink:0"
            >
              <el-icon><StarFilled v-if="isFav || q.favorited" /><Star v-else /></el-icon>
            </el-button>
          </div>
          <el-button text type="primary" size="small" @click="q._show = !q._show">
            {{ q._show ? '隐藏答案 ▲' : '查看答案 ▼' }}
          </el-button>
          <div v-if="q._show" class="q-detail">
            <div v-if="q.answer"><strong>答案：</strong>{{ q.answer }}</div>
            <div v-if="q.answer_guide"><strong>思路：</strong>{{ q.answer_guide }}</div>
            <div v-if="q.answer_script"><strong>话术：</strong>{{ q.answer_script }}</div>
            <div v-if="q.tags?.length" style="margin-top:0.4rem">
              <el-tag v-for="t in q.tags" :key="t" size="small" round style="margin-right:4px">{{ t }}</el-tag>
            </div>
          </div>
        </div>
      `
    }
  }
}
</script>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import NavBar from '../components/layout/NavBar.vue'
import {
  generatePracticeQuestions, savePracticeQuestions,
  browseQuestions, toggleFavorite, getFavorites,
} from '../api/practice'

const auth = useAuthStore()
const activeTab = ref('generate')

const difficulties = ['入门', '基础', '中等', '面试高频', '深度深挖']
const questionTypes = ['选择题', '简答题', '项目手撕题', '场景面试题', '压力面试题']

const genPosition = ref('')
const genDifficulty = ref('中等')
const genTypes = ref(['简答题', '场景面试题'])
const genCount = ref(5)
const generating = ref(false)
const saving = ref(false)
const generatedQuestions = ref([])

async function handleGenerate() {
  if (!genPosition.value.trim()) { ElMessage.error('请输入目标岗位'); return }
  generating.value = true
  try {
    const { data } = await generatePracticeQuestions({
      target_position: genPosition.value.trim(),
      difficulty: genDifficulty.value,
      question_types: genTypes.value,
      question_count: genCount.value,
    })
    generatedQuestions.value = (data.questions || []).map(q => ({ ...q, _show: false }))
    ElMessage.success(`已生成 ${generatedQuestions.value.length} 道题目`)
  } catch { ElMessage.error('生成失败，请检查 API 配置') }
  finally { generating.value = false }
}

async function handleSaveAll() {
  saving.value = true
  try {
    const { data } = await savePracticeQuestions({ position: genPosition.value.trim(), questions: generatedQuestions.value })
    // Assign real DB IDs so questions can be favorited
    const savedMap = {}
    ;(data.questions || []).forEach(s => { savedMap[s.question] = s.id })
    generatedQuestions.value.forEach(q => {
      if (savedMap[q.question]) q.id = savedMap[q.question]
    })
    ElMessage.success('已存入题库，切换到「题库浏览」查看')
    // Refresh browse list in background
    browsePage.value = 1
    loadBrowse()
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

const filterPosition = ref('')
const filterDifficulty = ref('')
const filterType = ref('')
const browsePage = ref(1)
const browseList = ref([])
const browseTotal = ref(0)

async function loadBrowse() {
  try {
    const params = { page: browsePage.value, page_size: 20 }
    if (filterPosition.value) params.position = filterPosition.value
    if (filterDifficulty.value) params.difficulty = filterDifficulty.value
    if (filterType.value) params.question_type = filterType.value
    const { data } = await browseQuestions(params)
    browseList.value = (data.questions || []).map(q => ({ ...q, _show: false }))
    browseTotal.value = data.total || 0
  } catch { /* */ }
}

async function handleFavorite(q) {
  try {
    await toggleFavorite(q.id)
    q.favorited = !q.favorited
    ElMessage.success(q.favorited ? '已收藏' : '已取消收藏')
    if (q.favorited) {
      // Add to favorites list for current session
      if (!favList.value.find(f => f.id === q.id)) {
        favList.value.push({ ...q, _show: false })
      }
    } else {
      favList.value = favList.value.filter(f => f.id !== q.id)
    }
  } catch { ElMessage.error('操作失败') }
}

const favList = ref([])
async function loadFavorites() {
  try {
    const { data } = await getFavorites()
    favList.value = (data.questions || []).map(q => ({ ...q, _show: false }))
  } catch { /* */ }
}

onMounted(() => {
  loadBrowse()
  if (auth.isLoggedIn) loadFavorites()
})

watch(activeTab, (tab) => {
  if (tab === 'browse') loadBrowse()
  if (tab === 'favorites' && auth.isLoggedIn) loadFavorites()
})
</script>

<style scoped>
.practice-page { min-height: 100vh; background: var(--bg-page); }
.main-content { padding: 80px 1.5rem 2rem; max-width: 1100px; margin: 0 auto; }
.page-title {
  font-size: 1.7rem; color: var(--text-primary); margin-bottom: 1.5rem;
  display: flex; align-items: center; font-weight: 700;
}

.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
}

.main-tabs :deep(.el-tabs__content) { padding: 1.25rem; }
.tab-label { display: flex; align-items: center; gap: 4px; }

.gen-card { padding: 1.5rem; margin-bottom: 1rem; }

.filter-bar {
  display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: center;
  padding: 1rem 1.5rem;
}

.q-section { margin-top: 1rem; }
.section-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem; color: var(--text-primary); font-weight: 700;
  font-size: 0.95rem;
}

.q-card { padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.q-top { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.q-idx {
  background: var(--green-600); color: #fff;
  border-radius: 6px; padding: 2px 8px;
  font-size: 0.78rem; flex-shrink: 0; font-weight: 700;
}
.q-text { font-weight: 600; color: var(--text-primary); flex: 1; min-width: 200px; margin-left: 0.5rem; }
.q-detail {
  margin-top: 0.75rem; padding: 0.85rem;
  background: var(--bg-subtle); border-radius: var(--radius-md);
  font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;
}
.q-detail div { margin-top: 0.35rem; }

@media (max-width: 768px) {
  .main-content { padding: 70px 1rem 1.5rem; }
  .page-title { font-size: 1.4rem; }

  /* Filter bar */
  .filter-bar {
    flex-wrap: wrap;
    padding: 0.75rem 1rem;
  }
  .filter-bar .el-input,
  .filter-bar .el-select,
  .filter-bar .el-button {
    width: 100% !important;
    flex: 1 1 100%;
  }

  /* Generate card - form inline to stack */
  .gen-card { padding: 1rem; }
  .gen-card :deep(.el-form--inline) {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }
  .gen-card :deep(.el-form--inline .el-form-item) {
    margin-right: 0;
  }
  .gen-card :deep(.el-form--inline .el-input),
  .gen-card :deep(.el-form--inline .el-select) {
    width: 100% !important;
  }

  .section-head { flex-direction: column; gap: 0.5rem; align-items: flex-start; }

  .q-card { padding: 0.75rem 1rem; }
  .q-text { margin-left: 0; font-size: 0.88rem; }
  .q-detail { font-size: 0.85rem; }

  .main-tabs :deep(.el-tabs__content) { padding: 0.75rem; }
}

@media (max-width: 480px) {
  .main-content { padding: 64px 0.6rem 1rem; }
  .page-title { font-size: 1.15rem; }

  .main-tabs :deep(.el-tabs__item) {
    font-size: 0.78rem;
    padding: 0 0.45rem;
  }
  .main-tabs :deep(.el-tabs__content) { padding: 0.6rem; }

  .gen-card { padding: 0.75rem; }
  .q-card { padding: 0.6rem 0.75rem; }
  .q-text { font-size: 0.82rem; }
  .q-detail { font-size: 0.78rem; }

  .section-head { gap: 0.35rem; }
  .section-head h2 { font-size: 0.95rem; }
}
</style>
