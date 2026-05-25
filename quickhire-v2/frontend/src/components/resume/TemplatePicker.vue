<template>
  <el-dialog
    v-model="visible"
    title="导出简历 PDF"
    width="780px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="tp-container">
      <!-- Template selection -->
      <div class="tp-section">
        <h4>选择模板</h4>
        <div class="tp-grid">
          <div
            v-for="t in templates"
            :key="t.id"
            class="tp-card"
            :class="{ active: selectedTemplate === t.id }"
            @click="selectedTemplate = t.id"
          >
            <div class="tp-thumb" :class="'thumb-' + t.id">
              <div class="thumb-inner">
                <div class="thumb-photo" v-if="photoPreview"></div>
                <div class="thumb-name"></div>
                <div class="thumb-lines" v-for="i in 4" :key="i"></div>
              </div>
            </div>
            <div class="tp-name">{{ t.name }}</div>
            <div class="tp-desc">{{ t.description }}</div>
            <div class="tp-check" v-if="selectedTemplate === t.id">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Photo upload -->
      <div class="tp-section">
        <h4>照片（可选）</h4>
        <div class="photo-row">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            @change="handlePhotoChange"
            class="photo-upload"
          >
            <div class="photo-drop" v-if="!photoPreview">
              <el-icon :size="28"><Plus /></el-icon>
              <span>上传照片</span>
            </div>
            <div class="photo-preview-wrap" v-else>
              <img :src="photoPreview" class="photo-preview-img" />
              <div class="photo-overlay">
                <el-icon><EditPen /></el-icon>
                <span>更换</span>
              </div>
            </div>
          </el-upload>
          <el-button v-if="photoPreview" text type="danger" size="small" @click="removePhoto">
            <el-icon><Delete /></el-icon> 移除照片
          </el-button>
        </div>
      </div>

      <!-- Page limit -->
      <div class="tp-section">
        <h4>篇幅控制</h4>
        <div class="page-limit-row">
          <el-radio-group v-model="pageLimit" size="large">
            <el-radio-button :value="1">
              1 页
              <el-tag v-if="recommendedPages > 1" type="danger" size="small" effect="dark" class="page-tag">需压缩</el-tag>
            </el-radio-button>
            <el-radio-button :value="2">
              2 页
              <el-tag v-if="recommendedPages === 1" type="success" size="small" effect="dark" class="page-tag">充裕</el-tag>
            </el-radio-button>
            <el-radio-button :value="null">
              不限
              <el-tag v-if="recommendedPages === 1" type="info" size="small" effect="dark" class="page-tag">推荐</el-tag>
            </el-radio-button>
          </el-radio-group>

          <div class="page-hint" v-if="pageLimit !== null && pageLimit < recommendedPages">
            <el-alert type="warning" :closable="false" show-icon>
              内容较多，压缩为 {{ pageLimit }} 页可能精简部分内容
            </el-alert>
          </div>
          <div class="page-info" v-else>
            当前约 {{ charCount }} 字，推荐 {{ recommendedPages }} 页
          </div>
        </div>
      </div>

      <!-- Live preview -->
      <div class="tp-section">
        <h4>预览效果</h4>
        <div class="tp-preview">
          <div class="preview-page">
            <div class="pv-header">
              <div class="pv-photo" v-if="photoPreview" :style="{ backgroundImage: 'url(' + photoPreview + ')' }"></div>
              <div class="pv-name">{{ candidateName || '姓名' }}</div>
              <div class="pv-contact" v-if="contactPreview">{{ contactPreview }}</div>
            </div>
            <div class="pv-section" v-for="(s, i) in previewSections.slice(0, 3)" :key="i">
              <div class="pv-section-title">{{ s.title }}</div>
              <div class="pv-line" v-for="(l, j) in s.lines.slice(0, 2)" :key="j">{{ l }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleExport" :loading="exporting">
        <el-icon style="margin-right:4px"><Download /></el-icon>
        导出 PDF
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  resumeText: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// Templates
const templates = ref([])
const selectedTemplate = ref(1)

onMounted(async () => {
  try {
    const { data } = await api.get('/resume/templates')
    templates.value = data
  } catch {
    templates.value = [
      { id: 1, name: '经典双栏', description: '左侧个人信息+照片，右侧经历内容' },
      { id: 2, name: '简洁单栏', description: '顶部头像与姓名，下方通栏排版' },
      { id: 3, name: '现代卡片', description: '模块独立卡片，头像右上角' },
      { id: 4, name: '创意侧边栏', description: '深色侧边栏，醒目有设计感' },
      { id: 5, name: '极简线条', description: '纯文字左对齐，细线分割' },
    ]
  }
})

// Photo
const photoPreview = ref(null)
const photoFile = ref(null)

function handlePhotoChange(file) {
  photoFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => { photoPreview.value = e.target.result }
  reader.readAsDataURL(file.raw)
}

function removePhoto() {
  photoPreview.value = null
  photoFile.value = null
}

// Page
const charCount = computed(() => props.resumeText.replace(/\s/g, '').length)
const recommendedPages = computed(() => charCount.value > 750 ? 2 : 1)
const pageLimit = ref(null)

// Preview
const candidateName = computed(() => {
  const first = props.resumeText.split('\n').find(l => l.trim())
  if (!first) return ''
  return first.split(/[|｜]/)[0]?.replace(/[：:，,。●◆\s]+$/, '').slice(0, 20) || ''
})

const contactPreview = computed(() => {
  const lines = props.resumeText.split('\n').slice(0, 5)
  const email = lines.find(l => l.includes('@'))
  const phone = lines.find(l => /1[3-9]\d{9}/.test(l))
  return [email, phone].filter(Boolean).map(l => l.trim()).join('  |  ')
})

const previewSections = computed(() => {
  const sectionPatterns = [
    { pattern: /教育[经历背景]*[：:]/i, title: '教育经历' },
    { pattern: /工作[经历经验]*[：:]/i, title: '工作经历' },
    { pattern: /项目[经历经验]*[：:]/i, title: '项目经验' },
    { pattern: /(?:专业)?技能[：:]?/i, title: '专业技能' },
  ]
  const sections = []
  const lines = props.resumeText.split('\n')
  let current = null
  for (const line of lines) {
    let matched = false
    for (const sp of sectionPatterns) {
      if (sp.pattern.test(line)) {
        if (current) sections.push(current)
        current = { title: sp.title, lines: [] }
        matched = true
        break
      }
    }
    if (!matched && current) {
      const t = line.trim()
      if (t) current.lines.push(t)
    }
  }
  if (current) sections.push(current)
  return sections
})

// Export
const exporting = ref(false)

async function handleExport() {
  if (!props.resumeText.trim()) {
    ElMessage.error('请先优化简历')
    return
  }

  exporting.value = true
  try {
    const fd = new FormData()
    fd.append('template_id', selectedTemplate.value)
    fd.append('content', props.resumeText)
    if (pageLimit.value !== null) fd.append('page_limit', pageLimit.value)
    if (photoFile.value) fd.append('photo', photoFile.value)

    const res = await api.post('/resume/export-pdf', fd, {
      responseType: 'blob',
      timeout: 60000,
    })

    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = '简历.pdf'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success('PDF 已生成并开始下载')
    visible.value = false
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    ElMessage.error('导出失败: ' + msg)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.tp-container { display: flex; flex-direction: column; gap: 1.25rem; max-height: 65vh; overflow-y: auto; padding-right: 4px; }

.tp-section h4 {
  font-size: 0.9rem; font-weight: 700; color: var(--text-primary);
  margin: 0 0 0.75rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border-light);
}

/* Template grid */
.tp-grid { display: flex; gap: 0.75rem; overflow-x: auto; padding-bottom: 0.5rem; }
.tp-card {
  flex: 0 0 120px; cursor: pointer; border-radius: var(--radius-md);
  padding: 0.5rem; border: 2px solid var(--border-default);
  transition: all var(--duration-fast) var(--ease-out);
  position: relative; text-align: center;
}
.tp-card:hover { border-color: var(--green-300); }
.tp-card.active { border-color: var(--green-500); background: var(--green-50); }

.tp-thumb {
  height: 100px; background: #f9fafb; border-radius: 4px;
  overflow: hidden; padding: 6px; margin-bottom: 0.35rem;
}
.thumb-inner { height: 100%; display: flex; flex-direction: column; gap: 2px; }
.thumb-photo { width: 14px; height: 14px; border-radius: 50%; background: var(--green-200); }
.thumb-name { width: 50%; height: 5px; background: var(--green-400); border-radius: 2px; }
.thumb-lines { height: 4px; background: #e0e0e0; border-radius: 2px; width: 100%; }

.tp-name { font-size: 0.78rem; font-weight: 600; color: var(--text-primary); }
.tp-desc { font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; }
.tp-check {
  position: absolute; top: -6px; right: -6px;
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--green-500); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 12px;
}

/* Photo */
.photo-row { display: flex; align-items: center; gap: 0.75rem; }
.photo-drop {
  width: 80px; height: 80px; border: 2px dashed var(--border-default);
  border-radius: var(--radius-md); display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px;
  color: var(--text-muted); font-size: 0.75rem; cursor: pointer;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.photo-drop:hover { border-color: var(--green-400); color: var(--green-600); }
.photo-preview-wrap {
  width: 80px; height: 80px; border-radius: var(--radius-md);
  overflow: hidden; position: relative; cursor: pointer;
}
.photo-preview-img { width: 100%; height: 100%; object-fit: cover; }
.photo-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 2px; color: #fff; font-size: 0.7rem;
  opacity: 0; transition: opacity var(--duration-fast) var(--ease-out);
}
.photo-preview-wrap:hover .photo-overlay { opacity: 1; }

/* Page */
.page-limit-row { display: flex; flex-direction: column; gap: 0.75rem; }
.page-tag { margin-left: 6px; vertical-align: middle; }
.page-info { font-size: 0.8rem; color: var(--text-muted); }

/* Preview */
.tp-preview {
  background: #fcfcfc; border: 1px solid var(--border-default);
  border-radius: var(--radius-md); padding: 1rem;
}
.preview-page {
  background: #fff; box-shadow: var(--shadow-sm);
  border-radius: 2px; padding: 1rem; min-height: 120px;
}
.pv-header { text-align: center; margin-bottom: 0.5rem; padding-bottom: 0.3rem; border-bottom: 1px solid #eee; }
.pv-photo {
  width: 30px; height: 30px; border-radius: 50%;
  background-size: cover; background-position: center;
  margin: 0 auto 0.2rem; background-color: var(--green-100);
}
.pv-name { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); }
.pv-contact { font-size: 0.65rem; color: var(--text-muted); margin-top: 1px; }
.pv-section-title {
  font-size: 0.7rem; font-weight: 700;
  color: var(--green-700); margin: 6px 0 2px;
}
.pv-line {
  font-size: 0.62rem; color: var(--text-secondary);
  line-height: 1.4; margin-bottom: 1px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
</style>
