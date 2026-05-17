<template>
  <div class="profile-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">👤 个人中心</h1>

      <el-tabs type="border-card">
        <!-- API Config -->
        <el-tab-pane label="🔑 API 配置">
          <el-form label-width="120px">
            <el-form-item label="API Key">
              <el-input v-model="apiKey" type="password" show-password placeholder="输入 DashScope API Key" />
            </el-form-item>
            <el-form-item label="模型">
              <el-select v-model="apiModel">
                <el-option v-for="m in models" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveApiConfig">保存配置</el-button>
              <el-button @click="testApi">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Profile Info -->
        <el-tab-pane label="👤 个人信息">
          <el-form label-width="100px">
            <el-form-item label="昵称">
              <el-input v-model="profile.name" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profile.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profile.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Change Password -->
        <el-tab-pane label="🔒 修改密码">
          <el-form label-width="100px">
            <el-form-item label="原密码">
              <el-input v-model="pw.old" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pw.new1" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="pw.new2" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Resume History -->
        <el-tab-pane label="📄 简历历史">
          <el-table :data="history" v-if="history.length">
            <el-table-column prop="version_number" label="版本" width="80" />
            <el-table-column prop="target_position" label="目标岗位" />
            <el-table-column prop="optimization_style" label="优化风格" />
            <el-table-column prop="created_at" label="创建时间" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button text type="primary" @click="loadResume(row)">加载</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无简历" />
        </el-tab-pane>

        <!-- Data Export -->
        <el-tab-pane label="💾 数据导出">
          <p>导出所有个人数据（简历、面试记录、求职记录）为 JSON 格式。</p>
          <el-button type="primary" @click="exportData">导出 JSON</el-button>
        </el-tab-pane>

        <!-- Preferences -->
        <el-tab-pane label="⚙️ 偏好设置">
          <el-form label-width="120px">
            <el-form-item label="默认优化风格">
              <el-select v-model="prefs.optimization_style">
                <el-option v-for="s in styles" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认面试难度">
              <el-select v-model="prefs.interview_difficulty">
                <el-option v-for="d in difficulties" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认题目数量">
              <el-input-number v-model="prefs.question_count" :min="3" :max="15" />
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

const apiKey = ref('')
const apiModel = ref('qwen-plus')
const models = ['qwen-turbo', 'qwen-plus', 'qwen-max']
const styles = ['简洁专业', '突出业绩', '技术导向', '创新风格']
const difficulties = ['入门', '基础', '中等', '面试高频', '深度深挖']

const profile = reactive({ name: '', email: '', phone: '' })
const pw = reactive({ old: '', new1: '', new2: '' })
const history = ref([])
const prefs = reactive({ optimization_style: '简洁专业', interview_difficulty: '中等', question_count: 5 })

onMounted(async () => {
  profile.name = auth.user?.display_name || ''
  profile.email = auth.user?.email || ''
  profile.phone = auth.user?.phone || ''
  await loadHistory()
  try {
    const { data } = await api.get('/profile/preferences')
    if (data.optimization_style) prefs.optimization_style = data.optimization_style
    if (data.interview_difficulty) prefs.interview_difficulty = data.interview_difficulty
    if (data.question_count) prefs.question_count = data.question_count
    if (data.api_model) apiModel.value = data.api_model
    if (data.api_key) apiKey.value = '••••••••'
  } catch { /* not configured yet */ }
  try {
    const { data } = await api.get('/profile/api-config')
    if (data.api_key) apiKey.value = '••••••••'
    if (data.api_model) apiModel.value = data.api_model
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
    },
  })
  ElMessage.success('API 配置已保存')
}

async function testApi() {
  try {
    const { data } = await api.post('/profile/test-api')
    ElMessage.success(data.connected ? 'API 连接成功！' : 'API 连接失败')
  } catch { ElMessage.error('测试失败') }
}

async function updateProfile() {
  await api.patch('/profile/info', {
    display_name: profile.name,
    email: profile.email,
    phone: profile.phone,
  })
  ElMessage.success('个人信息已更新')
}

async function changePassword() {
  if (pw.new1 !== pw.new2) {
    ElMessage.error('两次密码不一致')
    return
  }
  await api.patch('/profile/password', { old_password: pw.old, new_password: pw.new1 })
  ElMessage.success('密码已修改')
  pw.old = pw.new1 = pw.new2 = ''
}

async function savePrefs() {
  await api.put('/profile/preferences', { preferences: { ...prefs } })
  ElMessage.success('偏好已保存')
}

async function exportData() {
  const { data } = await api.get('/profile/export')
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'quickhire-export.json'; a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('数据已导出')
}

function loadResume(row) {
  resumeStore.resumeText = row.original_content
  resumeStore.optimizedResult = { optimized_text: row.optimized_content, diagnosis: row.analysis_result }
  ElMessage.success('已加载简历')
}
</script>

<style scoped>
.profile-page { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 900px; margin: 0 auto; }
.page-title { font-size: 1.8rem; color: #0f766e; margin-bottom: 1.5rem; }
</style>
