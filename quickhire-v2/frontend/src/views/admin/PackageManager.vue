<template>
  <div>
    <div class="page-header"><h2>套餐管理</h2></div>
    <div class="table-toolbar"><el-button type="primary" @click="openDialog(null)">新增套餐</el-button></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="name" label="名称" width="160" />
      <el-table-column prop="price" label="价格" width="100"><template #default="{ row }">¥{{ row.price }}</template></el-table-column>
      <el-table-column prop="duration_days" label="时长(天)" width="100" />
      <el-table-column prop="optimize_limit" label="优化次数" width="100" />
      <el-table-column prop="diagnose_limit" label="诊断次数" width="100" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" text @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)"><template #reference><el-button size="small" text type="danger">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑套餐' : '新增套餐'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" /></el-form-item>
        <el-form-item label="时长(天)"><el-input-number v-model="form.duration_days" :min="1" /></el-form-item>
        <el-form-item label="优化次数"><el-input-number v-model="form.optimize_limit" :min="0" /></el-form-item>
        <el-form-item label="诊断次数"><el-input-number v-model="form.diagnose_limit" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getPackages, createPackage, updatePackage, deletePackage } from '../../api/admin/packages'
import { ElMessage } from 'element-plus'
const items = ref([]), loading = ref(false), dialogVisible = ref(false), editingId = ref(null)
const form = reactive({ name: '', description: '', price: 0, duration_days: 30, optimize_limit: 10, diagnose_limit: 10, is_active: true, sort_order: 0 })
async function load() { loading.value = true; try { const { data } = await getPackages(); items.value = data.items } finally { loading.value = false } }
function openDialog(row) {
  editingId.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { name: '', description: '', price: 0, duration_days: 30, optimize_limit: 10, diagnose_limit: 10, is_active: true, sort_order: 0 })
  dialogVisible.value = true
}
async function handleSave() {
  if (editingId.value) await updatePackage(editingId.value, { ...form }); else await createPackage({ ...form })
  ElMessage.success('已保存'); dialogVisible.value = false; load()
}
async function handleDelete(id) { await deletePackage(id); ElMessage.success('已删除'); load() }
onMounted(load)
</script>
