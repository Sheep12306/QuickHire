<template>
  <div>
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理平台所有注册用户</p>
    </div>

    <div class="table-toolbar">
      <el-input v-model="search" placeholder="搜索邮箱/昵称/手机号" clearable style="width:240px" @clear="loadUsers" @keyup.enter="loadUsers" />
      <el-select v-model="filterRole" placeholder="角色" clearable style="width:140px" @change="loadUsers">
        <el-option label="普通用户" value="user" />
        <el-option label="超级管理员" value="super_admin" />
        <el-option label="运营管理" value="operator" />
        <el-option label="只读查看" value="viewer" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width:120px" @change="loadUsers">
        <el-option label="正常" value="active" />
        <el-option label="已封禁" value="banned" />
      </el-select>
      <el-button type="primary" @click="loadUsers">查询</el-button>
      <div class="spacer" />
      <el-button @click="handleExport">导出CSV</el-button>
    </div>

    <el-table :data="users" v-loading="loading" stripe @row-click="goDetail" style="cursor:pointer">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="display_name" label="昵称" min-width="120" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'super_admin' ? 'danger' : row.role === 'operator' ? 'warning' : row.role === 'viewer' ? 'info' : ''" size="small">
            {{ roleLabel(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="membership_type" label="会员" width="90">
        <template #default="{ row }">
          <el-tag :type="row.membership_type === 'premium' ? 'warning' : 'info'" size="small" effect="plain">
            {{ row.membership_type === 'premium' ? '付费' : '免费' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="resume_count" label="简历数" width="80" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <span class="status-dot" :class="row.is_active ? 'active' : 'inactive'" />
          {{ row.is_active ? '正常' : '封禁' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="110">
        <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click.stop="goDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :page-size="size"
      :total="total"
      layout="prev, pager, next, total"
      @current-change="loadUsers"
      style="margin-top:16px;justify-content:flex-end"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUsers, exportUsers } from '../../api/admin/users'

const router = useRouter()
const users = ref([])
const loading = ref(false)
const search = ref('')
const filterRole = ref('')
const filterStatus = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

function roleLabel(r) {
  const map = { super_admin: '超级管理员', operator: '运营', viewer: '只读', user: '用户' }
  return map[r] || r
}

function goDetail(row) {
  router.push(`/admin/users/${row.id}`)
}

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await getUsers({
      page: page.value,
      size: size.value,
      search: search.value,
      role: filterRole.value,
      status: filterStatus.value,
    })
    users.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  const { data } = await exportUsers()
  const csv = [Object.keys(data.items[0] || {}).join(','), ...data.items.map(r => Object.values(r).join(','))].join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `users_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
}

onMounted(loadUsers)
</script>
