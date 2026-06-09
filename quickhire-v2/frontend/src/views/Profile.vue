<template>
  <div class="profile-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">
        <el-icon style="margin-right:8px"><UserFilled /></el-icon>
        个人中心
      </h1>

      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        <!-- Profile Info -->
        <el-tab-pane name="info">
          <template #label>
            <span class="tab-label">
              <el-icon><User /></el-icon> 个人信息
            </span>
          </template>
          <el-form label-width="110px" class="profile-form">
            <el-form-item label="昵称">
              <el-input v-model="profile.name" size="large" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profile.email" size="large" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profile.phone" size="large" />
            </el-form-item>
            <el-form-item label="求职意向">
              <el-input v-model="profile.job_preference" size="large" placeholder="如：前端开发工程师、产品经理" />
            </el-form-item>
            <el-form-item label="所在城市">
              <el-input v-model="profile.city" size="large" placeholder="如：北京" />
            </el-form-item>
            <el-form-item label="意向城市">
              <el-input v-model="profile.target_city" size="large" placeholder="如：上海、杭州" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Favorites -->
        <el-tab-pane name="favorites">
          <template #label>
            <span class="tab-label">
              <el-icon><Star /></el-icon> 我的收藏
            </span>
          </template>
          <div v-if="favorites.length" class="table-responsive">
            <el-table :data="favorites" style="width:100%">
              <el-table-column prop="question" label="题目" min-width="200" show-overflow-tooltip />
              <el-table-column prop="position" label="岗位" width="100" />
              <el-table-column prop="type" label="题型" width="80" />
              <el-table-column prop="difficulty" label="难度" width="70" />
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ row }">
                  <el-button text type="danger" size="small" @click="removeFavorite(row)">
                    取消收藏
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else description="暂无收藏" />
        </el-tab-pane>

        <!-- API Config -->
        <el-tab-pane name="api">
          <template #label>
            <span class="tab-label">
              <el-icon><Key /></el-icon> API 配置
            </span>
          </template>
          <el-form label-width="120px" class="profile-form">
            <el-form-item label="服务商">
              <el-select v-model="apiProvider" size="large" @change="onProviderChange" style="width:100%">
                <el-option v-for="p in providers" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="API 地址">
              <el-input v-model="apiBaseUrl" size="large" placeholder="API 端点地址" />
            </el-form-item>
            <el-form-item label="模型">
              <el-select
                v-if="apiProvider !== 'custom'"
                v-model="apiModel"
                size="large"
                style="width:100%"
                filterable
                allow-create
              >
                <el-option v-for="m in currentModels" :key="m" :label="m" :value="m" />
              </el-select>
              <el-input
                v-else
                v-model="apiModel"
                size="large"
                placeholder="输入模型名称"
              />
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="apiKey" type="password" show-password placeholder="输入 API Key" size="large" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveApiConfig">保存配置</el-button>
              <el-button @click="testApi">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Resume History -->
        <el-tab-pane name="history">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon> 简历历史
            </span>
          </template>
          <div v-if="history.length" class="table-responsive">
            <el-table :data="history">
              <el-table-column prop="version_number" label="版本" width="60" />
              <el-table-column prop="target_position" label="目标岗位" min-width="120" show-overflow-tooltip />
              <el-table-column prop="optimization_style" label="优化风格" min-width="100" show-overflow-tooltip />
              <el-table-column prop="created_at" label="创建时间" min-width="100" show-overflow-tooltip />
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button text type="primary" size="small" @click="loadResume(row)">加载</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else description="暂无简历" />
        </el-tab-pane>

        <!-- Preferences -->
        <el-tab-pane name="prefs">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon> 偏好设置
            </span>
          </template>
          <el-form label-width="130px" class="profile-form">
            <el-form-item label="默认优化风格">
              <el-select v-model="prefs.optimization_style" size="large">
                <el-option v-for="s in styles" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认面试难度">
              <el-select v-model="prefs.interview_difficulty" size="large">
                <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认题目数量">
              <el-input-number v-model="prefs.question_count" :min="3" :max="15" size="large" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="savePrefs">保存偏好</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useResumeStore } from '../stores/resume'
import NavBar from '../components/layout/NavBar.vue'
import api from '../api'

const auth = useAuthStore()
const resumeStore = useResumeStore()
const activeTab = ref('info')

// ── Provider / API Config ──────────────────────────────
const providers = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com/v1/chat/completions',
    models: ['deepseek-chat', 'deepseek-reasoner', 'deepseek-v3', 'deepseek-v4', 'deepseek-pro'],
  },
  {
    id: 'kimi',
    name: 'Kimi (月之暗面)',
    baseUrl: 'https://api.moonshot.cn/v1/chat/completions',
    models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
  },
  {
    id: 'qwen',
    name: '通义千问',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    models: ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-plus-latest', 'qwen-max-latest'],
  },
  {
    id: 'glm',
    name: '智谱 GLM',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
    models: ['glm-4', 'glm-4-flash', 'glm-4-plus'],
  },
  {
    id: 'doubao',
    name: '字节豆包',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    models: ['doubao-pro-32k', 'doubao-lite-32k'],
  },
  {
    id: 'mimo',
    name: '小米 MiMo',
    baseUrl: 'https://api.mimo.xiaomi.com/v1/chat/completions',
    models: ['mimo-chat', 'mimo-pro'],
  },
  {
    id: 'qianfan',
    name: '百度千帆',
    baseUrl: 'https://qianfan.baidubce.com/v2/chat/completions',
    models: ['ernie-4.0-turbo-8k', 'ernie-3.5-8k', 'ernie-speed-8k'],
  },
  {
    id: 'custom',
    name: '自定义',
    baseUrl: '',
    models: [],
  },
]

const apiKey = ref('')
const apiModel = ref('deepseek-chat')
const apiBaseUrl = ref('')
const apiProvider = ref('deepseek')
const currentModels = ref([...providers[0].models])

function onProviderChange(providerId) {
  const p = providers.find(p => p.id === providerId)
  if (!p) return
  apiBaseUrl.value = p.baseUrl
  if (p.models.length > 0) {
    currentModels.value = [...p.models]
    apiModel.value = p.models[0]
  } else {
    // Custom: keep current model and allow the user to type freely
    currentModels.value = apiModel.value ? [apiModel.value] : []
  }
}

const styles = ['简洁专业', '突出业绩', '技术导向', '创新风格']
const difficulties = ['入门', '基础', '中等', '面试高频', '深度深挖']

const profile = reactive({ name: '', email: '', phone: '', job_preference: '', city: '', target_city: '' })
const history = ref([])
const favorites = ref([])
const prefs = reactive({ optimization_style: '简洁专业', interview_difficulty: '中等', question_count: 5 })

onMounted(async () => {
  profile.name = auth.user?.display_name || ''
  profile.email = auth.user?.email || ''
  profile.phone = auth.user?.phone || ''
  profile.job_preference = auth.user?.job_preference || ''
  profile.city = auth.user?.city || ''
  profile.target_city = auth.user?.target_city || ''
  await loadHistory()
  await loadFavorites()
  try {
    const { data } = await api.get('/profile/preferences')
    if (data.optimization_style) prefs.optimization_style = data.optimization_style
    if (data.interview_difficulty) prefs.interview_difficulty = data.interview_difficulty
    if (data.question_count) prefs.question_count = data.question_count
    if (data.api_model) apiModel.value = data.api_model
    if (data.api_key) apiKey.value = '••••••••'
  } catch { /* */ }
  try {
    const { data } = await api.get('/profile/api-config')
    if (data.api_key) apiKey.value = '••••••••'
    if (data.api_model) apiModel.value = data.api_model
    if (data.api_base_url) {
      apiBaseUrl.value = data.api_base_url
      // auto-detect provider from saved base_url
      const matched = providers.find(p => p.baseUrl === data.api_base_url)
      if (matched) {
        apiProvider.value = matched.id
        currentModels.value = [...matched.models]
        if (!matched.models.includes(data.api_model)) {
          currentModels.value = [...matched.models, data.api_model]
        }
      } else {
        apiProvider.value = 'custom'
        currentModels.value = data.api_model ? [data.api_model] : []
      }
    }
  } catch { /* */ }
})

async function loadHistory() {
  try {
    const { data } = await api.get('/resume/history')
    history.value = data
  } catch { /* */ }
}

async function saveApiConfig() {
  await api.put('/profile/api-config', {
    preferences: {
      api_key: apiKey.value !== '••••••••' ? apiKey.value : undefined,
      api_model: apiModel.value,
      api_base_url: apiBaseUrl.value,
    },
  })
  ElMessage.success('API 配置已保存')
}

async function testApi() {
  try {
    const { data } = await api.post('/profile/test-api', {
      api_key: apiKey.value !== '••••••••' ? apiKey.value : undefined,
      api_model: apiModel.value,
      api_base_url: apiBaseUrl.value,
    })
    ElMessage.success(data.success ? data.message : data.message || '未知结果')
  } catch { ElMessage.error('测试失败') }
}

async function updateProfile() {
  await api.patch('/profile/info', {
    display_name: profile.name,
    email: profile.email,
    phone: profile.phone,
    job_preference: profile.job_preference,
    city: profile.city,
    target_city: profile.target_city,
  })
  ElMessage.success('个人信息已更新')
}

async function savePrefs() {
  await api.put('/profile/preferences', { preferences: { ...prefs } })
  ElMessage.success('偏好已保存')
}

async function loadFavorites() {
  try {
    const { data } = await api.get('/practice/favorites')
    favorites.value = data.questions
  } catch { /* */ }
}

async function removeFavorite(row) {
  try {
    await api.post(`/practice/${row.id}/favorite`)
    favorites.value = favorites.value.filter(f => f.id !== row.id)
    ElMessage.success('已取消收藏')
  } catch { /* */ }
}

function loadResume(row) {
  resumeStore.resumeText = row.original_content
  resumeStore.optimizedResult = { optimized_text: row.optimized_content, diagnosis: row.analysis_result }
  ElMessage.success('已加载简历，请到简历优化页面查看')
}
</script>

<style scoped>
.profile-page { min-height: 100vh; background: var(--bg-page); }
.main-content { padding: 80px 1.5rem 2rem; max-width: 900px; margin: 0 auto; }
.page-title {
  font-size: 1.7rem; color: var(--text-primary);
  margin-bottom: 1.5rem; display: flex; align-items: center; font-weight: 700;
}

.main-tabs :deep(.el-tabs__content) {
  padding: 1.5rem;
}
.tab-label { display: flex; align-items: center; gap: 4px; }

.profile-form {
  max-width: 480px;
}
.profile-form :deep(.el-form-item__label) {
  text-align: left;
  justify-content: flex-start;
}
.tab-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* API 配置区：消除所有输入框的聚焦绿色外发光 */
.profile-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--border-default) inset !important;
}
.profile-form :deep(.el-input__inner:focus),
.profile-form :deep(.el-select__input:focus) {
  border-color: var(--border-default) !important;
  box-shadow: none !important;
  outline: none !important;
}

@media (max-width: 768px) {
  .main-content { padding: 70px 1rem 1.5rem; }
  .page-title { font-size: 1.4rem; }

  .profile-form { max-width: 100%; }
  .profile-form :deep(.el-form-item) {
    flex-direction: column;
    align-items: stretch;
  }
  .profile-form :deep(.el-form-item__label) {
    margin-bottom: 0.25rem;
    text-align: left;
  }
  .profile-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  .main-tabs :deep(.el-tabs__content) { padding: 1rem; }
}

@media (max-width: 480px) {
  .main-content { padding: 64px 0.6rem 1rem; }
  .page-title { font-size: 1.2rem; }

  .main-tabs :deep(.el-tabs__item) {
    font-size: 0.78rem;
    padding: 0 0.45rem;
  }
  .main-tabs :deep(.el-tabs__content) { padding: 0.75rem; }
  .tab-label { gap: 2px; }

  .profile-form :deep(.el-form-item) {
    margin-bottom: 0.75rem;
  }
  .profile-form :deep(.el-button) {
    width: 100%;
  }
}
</style>