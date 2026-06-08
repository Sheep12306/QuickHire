<template>
  <div>
    <div class="page-header"><h2>Prompt 模板管理</h2></div>
    <div class="table-toolbar"><el-button type="primary" @click="openDialog(null)">新增Prompt</el-button></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="name" label="名称" width="160" />
      <el-table-column prop="template_type" label="类型" width="120" />
      <el-table-column prop="content" label="内容" min-width="300">
        <template #default="{ row }">{{ row.content?.slice(0, 120) }}{{ row.content?.length > 120 ? '...' : '' }}</template>
      </el-table-column>
      <el-table-column prop="is_default" label="默认" width="80">
        <template #default="{ row }"><el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag></template>
      </el-table-column>
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
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑Prompt' : '新增Prompt'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.template_type" style="width:100%"><el-option label="optimize" value="optimize" /><el-option label="diagnose" value="diagnose" /><el-option label="quick-scan" value="quick-scan" /><el-option label="questions" value="questions" /><el-option label="coach" value="coach" /></el-select></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" rows="8" /></el-form-item>
        <el-form-item label="变量"><el-input v-model="form.variables" placeholder="JSON: {&quot;var1&quot;:&quot;说明&quot;}" /></el-form-item>
        <el-form-item label="默认"><el-switch v-model="form.is_default" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getPrompts, createPrompt, updatePrompt, deletePrompt } from '../../api/admin/content'
import { ElMessage } from 'element-plus'
const items = ref([]), loading = ref(false), dialogVisible = ref(false), editingId = ref(null)
const form = reactive({ name: '', template_type: 'optimize', content: '', variables: '', is_default: false, is_active: true })
async function load() { loading.value = true; try { const { data } = await getPrompts(); items.value = data.items } finally { loading.value = false } }
function openDialog(row) {
  editingId.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { name: '', template_type: 'optimize', content: '', variables: '', is_default: false, is_active: true })
  dialogVisible.value = true
}
async function handleSave() {
  if (editingId.value) await updatePrompt(editingId.value, { ...form }); else await createPrompt({ ...form })
  ElMessage.success('已保存'); dialogVisible.value = false; load()
}
async function handleDelete(id) { await deletePrompt(id); ElMessage.success('已删除'); load() }
onMounted(load)
</script>
