<template>
  <div>
    <div class="page-header">
      <el-button text @click="$router.push('/admin/resumes')">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2>简历详情 #{{ resume.id }}</h2>
    </div>

    <div v-loading="loading">
      <div class="detail-card">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户">{{ resume.user_name }} ({{ resume.user_email }})</el-descriptions-item>
          <el-descriptions-item label="目标岗位">{{ resume.target_position || '-' }}</el-descriptions-item>
          <el-descriptions-item label="优化风格">{{ resume.optimization_style || '-' }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ resume.version_number }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ resume.created_at }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Version Comparison -->
      <div class="detail-card" v-if="resume.original_content || resume.optimized_content">
        <h3>版本对比</h3>
        <div class="diff-container">
          <div class="diff-panel">
            <h4>原始简历</h4>
            <div>{{ resume.original_content || '无' }}</div>
          </div>
          <div class="diff-panel">
            <h4>优化后简历</h4>
            <div>{{ resume.optimized_content || '未优化' }}</div>
          </div>
        </div>
      </div>

      <!-- Analysis Result -->
      <div class="detail-card" v-if="resume.analysis_result">
        <h3>AI 分析结果</h3>
        <pre style="white-space:pre-wrap;font-size:13px;line-height:1.6">{{ resume.analysis_result }}</pre>
      </div>

      <!-- Version History -->
      <div class="detail-card" v-if="versions.length > 1">
        <h3>版本历史</h3>
        <el-table :data="versions" stripe>
          <el-table-column prop="version_number" label="版本" width="60" />
          <el-table-column prop="optimization_style" label="优化风格" width="100" />
          <el-table-column prop="created_at" label="时间" width="170" />
          <el-table-column prop="is_current" label="当前" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.is_current" type="success" size="small">当前</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getResumeDetail, getResumeVersions } from '../../api/admin/resumes'

const route = useRoute()
const resume = ref({})
const versions = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [detailRes, versRes] = await Promise.all([
      getResumeDetail(route.params.id),
      getResumeVersions(route.params.id),
    ])
    resume.value = detailRes.data
    versions.value = versRes.data.items || []
  } finally { loading.value = false }
})
</script>
