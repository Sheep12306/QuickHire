<template>
  <div>
    <div class="page-header"><h2>公告管理</h2></div>
    <div class="table-toolbar"><el-button type="primary" @click="openDialog(null)">新增公告</el-button></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="{ row }"><el-tag :type="row.priority === 'urgent' ? 'danger' : row.priority === 'high' ? 'warning' : 'info'" size="small">{{ row.priority }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="is_published" label="状态" width="80">
        <template #default="{ row }"><el-tag :type="row.is_published ? 'success' : 'info'" size="small">{{ row.is_published ? '已发布' : '草稿' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="110"><template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template></el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" text @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)"><template #reference><el-button size="small" text type="danger">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑公告' : '新增公告'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" rows="6" /></el-form-item>
        <el-form-item label="优先级"><el-select v-model="form.priority" style="width:100%"><el-option label="普通" value="normal" /><el-option label="重要" value="high" /><el-option label="紧急" value="urgent" /></el-select></el-form-item>
        <el-form-item label="发布"><el-switch v-model="form.is_published" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement } from '../../api/admin/content'
import { ElMessage } from 'element-plus'
const items = ref([]), loading = ref(false), dialogVisible = ref(false), editingId = ref(null)
const form = reactive({ title: '', content: '', priority: 'normal', is_published: false })
async function load() { loading.value = true; try { const { data } = await getAnnouncements(); items.value = data.items } finally { loading.value = false } }
function openDialog(row) {
  editingId.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { title: '', content: '', priority: 'normal', is_published: false })
  dialogVisible.value = true
}
async function handleSave() {
  if (editingId.value) await updateAnnouncement(editingId.value, { ...form }); else await createAnnouncement({ ...form })
  ElMessage.success('已保存'); dialogVisible.value = false; load()
}
async function handleDelete(id) { await deleteAnnouncement(id); ElMessage.success('已删除'); load() }
onMounted(load)
</script>
