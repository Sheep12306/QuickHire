<template>
  <div class="practice-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">📚 面试刷题中心</h1>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- Tab 1: AI Generate by Position -->
        <el-tab-pane label="🤖 AI 出题" name="generate">
          <div class="gen-card">
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
                  🤖 AI 生成
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <div v-if="generatedQuestions.length" class="q-section">
            <div class="section-head">
              <span>已生成 {{ generatedQuestions.length }} 道「{{ genPosition }}」面试题</span>
              <el-button type="success" @click="handleSaveAll" :loading="saving">💾 全部存入题库</el-button>
            </div>
            <div v-for="(q, i) in generatedQuestions" :key="'g'+i" class="q-card">
              <div class="q-top">
                <span class="q-idx">#{{ i + 1 }}</span>
                <el-tag v-if="q.type" size="small" effect="plain">{{ q.type }}</el-tag>
                <el-tag v-if="q.difficulty" size="small" effect="plain" style="margin-left:4px">{{ q.difficulty }}</el-tag>
                <span class="q-text">{{ q.question }}</span>
              </div>
              <el-button text type="primary" size="small" @click="q._show = !q._show">
                {{ q._show ? '▲ 隐藏答案' : '▼ 查看答案' }}
              </el-button>
              <div v-if="q._show" class="q-detail">
                <div v-if="q.answer"><strong>📝 答案：</strong>{{ q.answer }}</div>
                <div v-if="q.answer_guide"><strong>💡 思路：</strong>{{ q.answer_guide }}</div>
                <div v-if="q.answer_script"><strong>🎤 话术：</strong>{{ q.answer_script }}</div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: Browse Question Bank -->
        <el-tab-pane label="📋 题库浏览" name="browse">
          <div class="filter-bar">
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
            <div v-for="(q, i) in browseList" :key="q.id" class="q-card">
              <div class="q-top">
                <span class="q-idx">#{{ (browsePage - 1) * 20 + i + 1 }}</span>
                <el-tag v-if="q.type" size="small" effect="plain">{{ q.type }}</el-tag>
                <el-tag v-if="q.difficulty" size="small" effect="plain" style="margin-left:4px">{{ q.difficulty }}</el-tag>
                <el-tag v-if="q.position" size="small" effect="plain" type="info" style="margin-left:4px">{{ q.position }}</el-tag>
                <span class="q-text">{{ q.question }}</span>
                <el-button
                  :type="q.favorited ? 'warning' : 'default'"
                  size="small" circle
                  @click="handleFavorite(q)"
                  style="flex-shrink:0"
                >{{ q.favorited ? '⭐' : '☆' }}</el-button>
              </div>
              <el-button text type="primary" size="small" @click="q._show = !q._show">
                {{ q._show ? '▲ 隐藏答案' : '▼ 查看答案' }}
              </el-button>
              <div v-if="q._show" class="q-detail">
                <div v-if="q.answer"><strong>📝 答案：</strong>{{ q.answer }}</div>
                <div v-if="q.answer_guide"><strong>💡 思路：</strong>{{ q.answer_guide }}</div>
                <div v-if="q.tags?.length" style="margin-top:0.4rem">
                  <el-tag v-for="t in q.tags" :key="t" size="small" round style="margin-right:4px">{{ t }}</el-tag>
                </div>
              </div>
            </div>
            <el-pagination
              v-if="browseTotal > 20"
              :current-page="browsePage" :page-size="20" :total="browseTotal"
              layout="prev, pager, next" @current-change="(p) => { browsePage = p; loadBrowse() }"
              style="margin-top:1rem; justify-content:center"
            />
          </div>
          <el-empty v-else description="题库中暂无题目，先生成并保存一些吧" />
        </el-tab-pane>

        <!-- Tab 3: My Favorites -->
        <el-tab-pane label="⭐ 我的收藏" name="favorites" v-if="auth.isLoggedIn">
          <div v-if="favList.length" class="q-section">
            <div class="section-head">已收藏 {{ favList.length }} 道题目</div>
            <div v-for="(q, i) in favList" :key="'f'+q.id" class="q-card">
              <div class="q-top">
                <span class="q-idx">#{{ i + 1 }}</span>
                <el-tag v-if="q.type" size="small" effect="plain">{{ q.type }}</el-tag>
                <el-tag v-if="q.difficulty" size="small" effect="plain" style="margin-left:4px">{{ q.difficulty }}</el-tag>
                <span class="q-text">{{ q.question }}</span>
                <el-button type="warning" size="small" circle @click="handleFavorite(q)" style="flex-shrink:0">⭐</el-button>
              </div>
              <el-button text type="primary" size="small" @click="q._show = !q._show">
                {{ q._show ? '▲ 隐藏答案' : '▼ 查看答案' }}
              </el-button>
              <div v-if="q._show" class="q-detail">
                <div v-if="q.answer"><strong>📝 答案：</strong>{{ q.answer }}</div>
                <div v-if="q.answer_guide"><strong>💡 思路：</strong>{{ q.answer_guide }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="还没有收藏任何题目" />
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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

// Generate
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
    await savePracticeQuestions({ position: genPosition.value.trim(), questions: generatedQuestions.value })
    ElMessage.success('已存入题库')
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

// Browse
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
    if (!q.favorited) favList.value = favList.value.filter(f => f.id !== q.id)
  } catch { ElMessage.error('操作失败') }
}

// Favorites
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
</script>

<style scoped>
.practice-page { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 1100px; margin: 0 auto; }
.page-title { font-size: 1.8rem; color: #0f766e; margin-bottom: 1.5rem; }
.gen-card { background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #ccfbf1; margin-bottom: 1rem; }
.filter-bar { display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: center; background: #fff; border-radius: 12px; padding: 1rem 1.5rem; border: 1px solid #ccfbf1; }
.q-section { margin-top: 1rem; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; color: #0f766e; font-weight: 600; }
.q-card {
  background: #fff; border: 1px solid #ccfbf1; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.75rem;
  transition: box-shadow 0.15s;
}
.q-card:hover { box-shadow: 0 2px 12px rgba(15,118,110,0.06); }
.q-top { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.q-idx { background: #0d9488; color: #fff; border-radius: 4px; padding: 1px 6px; font-size: 0.8rem; flex-shrink: 0; }
.q-text { font-weight: 600; color: #0f766e; flex: 1; min-width: 200px; margin-left: 0.5rem; }
.q-detail { margin-top: 0.75rem; padding: 0.75rem; background: #f8fafb; border-radius: 8px; font-size: 0.9rem; color: #555; line-height: 1.6; }
.q-detail div { margin-top: 0.3rem; }
</style>
