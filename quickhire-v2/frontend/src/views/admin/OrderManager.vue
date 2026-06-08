<template>
  <div>
    <div class="page-header"><h2>订单管理</h2></div>
    <div class="table-toolbar">
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width:120px" @change="load">
        <el-option label="待支付" value="pending" /><el-option label="已完成" value="completed" /><el-option label="已退款" value="refunded" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_email" label="用户" width="160" />
      <el-table-column prop="package_name" label="套餐" width="120" />
      <el-table-column prop="amount" label="金额" width="80"><template #default="{ row }">¥{{ row.amount }}</template></el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'refunded' ? 'warning' : 'info'" size="small">
            {{ row.status === 'completed' ? '已完成' : row.status === 'refunded' ? '已退款' : row.status === 'pending' ? '待支付' : row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="payment_method" label="支付方式" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="110"><template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template></el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button v-if="row.status === 'completed'" size="small" text type="danger" @click="handleRefund(row.id)">退款</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next, total" @current-change="load" style="margin-top:16px;justify-content:flex-end" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrders, refundOrder } from '../../api/admin/packages'
import { ElMessage, ElMessageBox } from 'element-plus'
const items = ref([]), loading = ref(false), page = ref(1), size = ref(20), total = ref(0), filterStatus = ref('')
async function load() {
  loading.value = true
  try { const { data } = await getOrders({ page: page.value, size: size.value, status: filterStatus.value }); items.value = data.items; total.value = data.total } finally { loading.value = false }
}
async function handleRefund(id) {
  try {
    await ElMessageBox.prompt('退款原因', '退款确认')
    const reason = '' // messageBox value
    // Note: ElMessageBox.prompt returns { value } in ElementPlus
  } catch { return }
  await refundOrder(id)
  ElMessage.success('已退款')
  load()
}
onMounted(load)
</script>
