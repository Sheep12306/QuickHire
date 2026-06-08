<template>
  <div>
    <div class="page-header"><h2>错误日志</h2><p>API 调用异常记录</p></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="endpoint" label="接口" width="120" />
      <el-table-column prop="model" label="模型" width="120" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }"><el-tag type="danger" size="small">{{ row.status }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误信息" min-width="300" />
      <el-table-column prop="created_at" label="时间" width="170" />
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next, total" @current-change="load" style="margin-top:16px;justify-content:flex-end" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getErrorLogs } from '../../api/admin/logs'
const items = ref([]), loading = ref(false), page = ref(1), size = ref(50), total = ref(0)
async function load() {
  loading.value = true
  try { const { data } = await getErrorLogs({ page: page.value, size: size.value }); items.value = data.items; total.value = data.total } finally { loading.value = false }
}
onMounted(load)
</script>
