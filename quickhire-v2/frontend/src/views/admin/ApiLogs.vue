<template>
  <div>
    <div class="page-header"><h2>API 调用日志</h2><p>查看所有 AI API 请求记录</p></div>

    <div class="table-toolbar">
      <el-input v-model="filters.model" placeholder="模型名称" clearable style="width:160px" />
      <el-select v-model="filters.status" placeholder="状态" clearable style="width:120px" @change="load">
        <el-option label="成功" value="success" />
        <el-option label="失败" value="error" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_email" label="用户" width="150" />
      <el-table-column prop="endpoint" label="接口" width="120" />
      <el-table-column prop="model" label="模型" width="120" />
      <el-table-column label="Tokens" width="120">
        <template #default="{ row }">{{ row.prompt_tokens + row.completion_tokens }}</template>
      </el-table-column>
      <el-table-column prop="latency_ms" label="耗时" width="80">
        <template #default="{ row }">{{ row.latency_ms }}ms</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">{{ row.status === 'success' ? '成功' : '失败' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cost" label="成本" width="80">
        <template #default="{ row }">${{ row.cost?.toFixed(6) }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column prop="error_message" label="错误信息" min-width="200">
        <template #default="{ row }">
          <span v-if="row.error_message" style="color:var(--el-color-danger);font-size:12px">{{ row.error_message.slice(0, 100) }}</span>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="size" :total="total"
      layout="prev, pager, next, total" @current-change="load"
      style="margin-top:16px;justify-content:flex-end"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getApiCallLogs } from '../../api/admin/logs'

const items = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(50)
const total = ref(0)
const filters = reactive({ model: '', status: '' })

async function load() {
  loading.value = true
  try {
    const { data } = await getApiCallLogs({ page: page.value, size: size.value, ...filters })
    items.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

onMounted(load)
</script>
