<template>
  <div>
    <div class="page-header">
      <h2>简历管理</h2>
      <p>查看和管理所有用户的简历优化记录</p>
    </div>

    <div class="table-toolbar">
      <el-input v-model="searchPosition" placeholder="搜索目标岗位" clearable style="width:200px" @keyup.enter="load" />
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:260px" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe @row-click="goDetail" style="cursor:pointer">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="user_email" label="用户" min-width="160" />
      <el-table-column prop="target_position" label="目标岗位" min-width="140" />
      <el-table-column prop="optimization_style" label="优化风格" width="100" />
      <el-table-column prop="version_number" label="版本" width="60" />
      <el-table-column label="原始内容" min-width="200">
        <template #default="{ row }">{{ row.original_content?.slice(0, 80) }}{{ row.original_content?.length > 80 ? '...' : '' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="110">
        <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click.stop="goDetail(row)">详情</el-button>
          <el-popconfirm title="确定删除该简历记录？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" text type="danger" @click.stop>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :page-size="size"
      :total="total"
      layout="prev, pager, next, total"
      @current-change="load"
      style="margin-top:16px;justify-content:flex-end"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getResumes, deleteResume } from '../../api/admin/resumes'
import { ElMessage } from 'element-plus'

const router = useRouter()
const items = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const searchPosition = ref('')
const dateRange = ref([])

function goDetail(row) { router.push(`/admin/resumes/${row.id}`) }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value, target_position: searchPosition.value }
    if (dateRange.value?.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const { data } = await getResumes(params)
    items.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

async function handleDelete(id) {
  await deleteResume(id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>
