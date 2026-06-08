<template>
  <div>
    <div class="page-header">
      <el-button text @click="$router.push('/admin/users')">
        <el-icon><ArrowLeft /></el-icon> 返回用户列表
      </el-button>
      <h2>{{ user.display_name || user.email || '用户详情' }}</h2>
    </div>

    <el-tabs v-model="activeTab" v-loading="loading">
      <!-- Basic Info -->
      <el-tab-pane label="基本信息" name="info">
        <div class="detail-card" v-if="user.id">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ID">{{ user.id }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
            <el-descriptions-item label="手机">{{ user.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="昵称">{{ user.display_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="user.role === 'super_admin' ? 'danger' : user.role === 'operator' ? 'warning' : 'info'" size="small">
                {{ roleLabel(user.role) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <span class="status-dot" :class="user.is_active ? 'active' : 'inactive'" />
              {{ user.is_active ? '正常' : '已封禁' }}
              <span v-if="!user.is_active && user.ban_reason" style="color:var(--el-color-danger);margin-left:8px">原因: {{ user.ban_reason }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="会员类型">{{ user.membership_type === 'premium' ? '付费会员' : '免费用户' }}</el-descriptions-item>
            <el-descriptions-item label="会员到期">{{ user.membership_expires_at?.slice(0, 10) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="求职意向">{{ user.job_preference || '-' }}</el-descriptions-item>
            <el-descriptions-item label="城市">{{ user.city || '-' }}</el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ user.created_at?.slice(0, 10) }}</el-descriptions-item>
            <el-descriptions-item label="最后登录">{{ user.last_login_at?.slice(0, 10) || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div style="margin-top:16px">
            <span>统计：</span>
            <el-tag type="primary" size="small">简历 {{ user.resume_count }}</el-tag>
            <el-tag type="success" size="small" style="margin-left:8px">面试 {{ user.interview_count }}</el-tag>
            <el-tag type="warning" size="small" style="margin-left:8px">优化 {{ user.optimize_count }}</el-tag>
          </div>

          <div style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap">
            <el-button v-if="user.is_active" type="danger" @click="showBanDialog = true">封禁用户</el-button>
            <el-button v-else type="success" @click="handleUnban">解封用户</el-button>
            <el-dropdown @command="handleRoleChange">
              <el-button>修改角色</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="user">普通用户</el-dropdown-item>
                  <el-dropdown-item command="super_admin">超级管理员</el-dropdown-item>
                  <el-dropdown-item command="operator">运营管理</el-dropdown-item>
                  <el-dropdown-item command="viewer">只读查看</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="showResetPwd = true">重置密码</el-button>
            <el-button @click="showNoteDialog = true">添加备注</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- Notes -->
      <el-tab-pane label="管理员备注" name="notes">
        <div class="detail-card">
          <div v-if="notes.length === 0" style="color:var(--el-text-color-placeholder);padding:20px;text-align:center">暂无备注</div>
          <div v-for="n in notes" :key="n.id" style="padding:12px 0;border-bottom:1px solid var(--el-border-color-light)">
            <div style="font-size:13px;color:var(--el-text-color-secondary);margin-bottom:6px">
              {{ n.admin_name }} · {{ n.created_at }}
            </div>
            <div>{{ n.note }}</div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Audit Log -->
      <el-tab-pane label="操作记录" name="audit">
        <el-table :data="auditLogs" v-loading="auditLoading" stripe>
          <el-table-column prop="action" label="操作" width="140" />
          <el-table-column prop="detail" label="详情" min-width="200" />
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Ban Dialog -->
    <el-dialog v-model="showBanDialog" title="封禁用户" width="420px">
      <el-form>
        <el-form-item label="封禁原因">
          <el-input v-model="banReason" type="textarea" />
        </el-form-item>
        <el-form-item label="封禁时长">
          <el-select v-model="banDuration" style="width:100%">
            <el-option label="永久" :value="0" />
            <el-option label="1 小时" :value="1" />
            <el-option label="24 小时" :value="24" />
            <el-option label="7 天" :value="168" />
            <el-option label="30 天" :value="720" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBanDialog = false">取消</el-button>
        <el-button type="danger" @click="handleBan" :loading="banLoading">确认封禁</el-button>
      </template>
    </el-dialog>

    <!-- Reset Password Dialog -->
    <el-dialog v-model="showResetPwd" title="重置密码" width="400px">
      <el-input v-model="newPassword" placeholder="输入新密码" show-password />
      <template #footer>
        <el-button @click="showResetPwd = false">取消</el-button>
        <el-button type="primary" @click="handleResetPwd">确认</el-button>
      </template>
    </el-dialog>

    <!-- Note Dialog -->
    <el-dialog v-model="showNoteDialog" title="添加备注" width="400px">
      <el-input v-model="noteText" type="textarea" rows="4" placeholder="输入备注内容" />
      <template #footer>
        <el-button @click="showNoteDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddNote">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import {
  getUserDetail, banUser, unbanUser, changeUserRole,
  resetUserPassword, getUserNotes, addUserNote, getUserAuditLog,
} from '../../api/admin/users'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const user = ref({})
const loading = ref(false)
const activeTab = ref('info')
const notes = ref([])
const auditLogs = ref([])
const auditLoading = ref(false)

// Ban
const showBanDialog = ref(false)
const banReason = ref('')
const banDuration = ref(0)
const banLoading = ref(false)

// Reset password
const showResetPwd = ref(false)
const newPassword = ref('')

// Note
const showNoteDialog = ref(false)
const noteText = ref('')

function roleLabel(r) {
  const map = { super_admin: '超级管理员', operator: '运营', viewer: '只读', user: '用户' }
  return map[r] || r
}

async function loadUser() {
  loading.value = true
  try {
    const { data } = await getUserDetail(route.params.id)
    user.value = data
  } finally {
    loading.value = false
  }
}

async function loadNotes() {
  const { data } = await getUserNotes(route.params.id)
  notes.value = data.items
}

async function loadAudit() {
  auditLoading.value = true
  try {
    const { data } = await getUserAuditLog(route.params.id)
    auditLogs.value = data.items
  } finally {
    auditLoading.value = false
  }
}

async function handleBan() {
  banLoading.value = true
  try {
    await banUser(route.params.id, banReason.value, banDuration.value)
    ElMessage.success('已封禁')
    showBanDialog.value = false
    loadUser()
  } finally {
    banLoading.value = false
  }
}

async function handleUnban() {
  await unbanUser(route.params.id)
  ElMessage.success('已解封')
  loadUser()
}

async function handleRoleChange(role) {
  await changeUserRole(route.params.id, role)
  ElMessage.success('角色已更新')
  loadUser()
}

async function handleResetPwd() {
  if (newPassword.value.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  await resetUserPassword(route.params.id, newPassword.value)
  ElMessage.success('密码已重置')
  showResetPwd.value = false
  newPassword.value = ''
}

async function handleAddNote() {
  if (!noteText.value.trim()) return
  await addUserNote(route.params.id, noteText.value)
  ElMessage.success('备注已添加')
  showNoteDialog.value = false
  noteText.value = ''
  loadNotes()
}

onMounted(() => {
  loadUser()
  loadNotes()
  loadAudit()
})
</script>
