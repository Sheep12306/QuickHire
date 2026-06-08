<template>
  <div>
    <div class="page-header"><h2>帮助中心 / FAQ</h2></div>
    <div class="table-toolbar"><el-button type="primary" @click="openDialog(null)">新增文章</el-button></div>
    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="sort_order" label="排序" width="70" />
      <el-table-column prop="is_published" label="状态" width="80">
        <template #default="{ row }"><el-tag :type="row.is_published ? 'success' : 'info'" size="small">{{ row.is_published ? '已发布' : '草稿' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" text @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)"><template #reference><el-button size="small" text type="danger">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑文章' : '新增文章'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" rows="8" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="逗号分隔" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
        <el-form-item label="发布"><el-switch v-model="form.is_published" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getHelpArticles, createHelpArticle, updateHelpArticle, deleteHelpArticle } from '../../api/admin/content'
import { ElMessage } from 'element-plus'
const items = ref([]), loading = ref(false), dialogVisible = ref(false), editingId = ref(null)
const form = reactive({ title: '', content: '', category: '', tags: '', sort_order: 0, is_published: false })
async function load() { loading.value = true; try { const { data } = await getHelpArticles(); items.value = data.items } finally { loading.value = false } }
function openDialog(row) {
  editingId.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { title: '', content: '', category: '', tags: '', sort_order: 0, is_published: false })
  dialogVisible.value = true
}
async function handleSave() {
  if (editingId.value) await updateHelpArticle(editingId.value, { ...form }); else await createHelpArticle({ ...form })
  ElMessage.success('已保存'); dialogVisible.value = false; load()
}
async function handleDelete(id) { await deleteHelpArticle(id); ElMessage.success('已删除'); load() }
onMounted(load)
</script>
