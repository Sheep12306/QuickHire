<template>
  <div>
    <div class="page-header"><h2>会员管理</h2></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="display_name" label="昵称" width="120" />
      <el-table-column prop="membership_type" label="会员类型" width="100">
        <template #default="{ row }"><el-tag :type="row.membership_type === 'premium' ? 'warning' : 'info'" size="small">{{ row.membership_type || 'free' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="membership_expires_at" label="到期时间" width="120"><template #default="{ row }">{{ row.membership_expires_at?.slice(0, 10) || '-' }}</template></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="handleExtend(row.id)">延期</el-button>
          <el-button size="small" text type="danger" @click="handleCancel(row.id)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next, total" @current-change="load" style="margin-top:16px;justify-content:flex-end" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMemberships, extendMembership, cancelMembership } from '../../api/admin/packages'
import { ElMessage, ElMessageBox } from 'element-plus'
const items = ref([]), loading = ref(false), page = ref(1), size = ref(20), total = ref(0)
async function load() {
  loading.value = true
  try { const { data } = await getMemberships({ page: page.value, size: size.value }); items.value = data.items; total.value = data.total } finally { loading.value = false }
}
async function handleExtend(userId) {
  try { const { value } = await ElMessageBox.prompt('延期天数', '会员延期', { inputType: 'number', inputValue: '30' }); await extendMembership(userId, parseInt(value)); ElMessage.success('已延期'); load() } catch {}
}
async function handleCancel(userId) {
  try { await ElMessageBox.confirm('确定取消该用户会员？', '确认', { type: 'warning' }); await cancelMembership(userId); ElMessage.success('已取消'); load() } catch {}
}
onMounted(load)
</script>
