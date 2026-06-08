<template>
  <div>
    <div class="page-header"><h2>系统设置</h2></div>

    <el-tabs v-model="activeTab">
      <!-- Free Usage Config -->
      <el-tab-pane label="免费额度" name="usage">
        <div class="detail-card" v-loading="usageLoading">
          <h3>用户免费使用额度控制</h3>
          <p style="color:var(--el-text-color-secondary);margin-bottom:20px">控制未配置自有 API Key 的用户每日免费使用次数。不限次数模式适合推广期吸引用户，设限模式适合用户量增长后控制成本。</p>

          <el-form label-width="140px">
            <el-form-item label="不限次数模式">
              <el-switch v-model="usageUnlimited" active-text="开启（无限制）" inactive-text="关闭（按次数限制）" />
            </el-form-item>
            <el-form-item label="每日免费次数" v-if="!usageUnlimited">
              <el-input-number v-model="usageDailyLimit" :min="1" :max="100" :step="1" />
              <span style="margin-left:8px;color:var(--el-text-color-secondary)">次/天（含优化和诊断）</span>
            </el-form-item>
          </el-form>

          <el-divider />
          <el-descriptions :column="2" border>
            <el-descriptions-item label="当前模式">
              <el-tag :type="usageUnlimited ? 'success' : 'warning'" size="large">
                {{ usageUnlimited ? '不限次数' : `每日限 ${usageDailyLimit} 次` }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="生效时间">保存后立即生效</el-descriptions-item>
            <el-descriptions-item label="适用对象">未配置自有 API Key 的免费用户</el-descriptions-item>
            <el-descriptions-item label="付费/自有Key用户">不受限制</el-descriptions-item>
          </el-descriptions>

          <el-button type="primary" @click="saveUsageConfig" style="margin-top:16px" :loading="usageSaving">保存额度配置</el-button>
        </div>
      </el-tab-pane>

      <!-- General Config -->
      <el-tab-pane label="通用配置" name="general">
        <div class="detail-card" v-loading="configLoading">
          <el-table :data="configRows" stripe>
            <el-table-column prop="key" label="配置项" width="200" />
            <el-table-column label="值"><template #default="{ row }"><el-input v-model="row.value" /></template></el-table-column>
            <el-table-column prop="description" label="说明" min-width="200" />
          </el-table>
          <el-button type="primary" @click="saveConfig" style="margin-top:16px">保存配置</el-button>
        </div>
      </el-tab-pane>

      <!-- Roles -->
      <el-tab-pane label="角色权限" name="roles">
        <div class="detail-card" v-loading="rolesLoading">
          <h3>角色与权限说明</h3>
          <el-table :data="roles" stripe>
            <el-table-column prop="label" label="角色" width="120" />
            <el-table-column label="权限">
              <template #default="{ row }">
                <el-tag v-for="p in row.permissions" :key="p" size="small" style="margin:2px">{{ p }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- IP Whitelist -->
      <el-tab-pane label="IP 白名单" name="ip">
        <div class="detail-card" v-loading="ipLoading">
          <el-form-item label="启用IP白名单"><el-switch v-model="ipEnabled" /></el-form-item>
          <el-input v-model="ipListText" type="textarea" rows="4" placeholder="每行一个IP地址" style="margin-top:12px" />
          <el-button type="primary" @click="saveIpWhitelist" style="margin-top:12px">保存</el-button>
        </div>
      </el-tab-pane>

      <!-- Audit Log -->
      <el-tab-pane label="操作审计" name="audit">
        <el-table :data="auditLogs" v-loading="auditLoading" stripe>
          <el-table-column prop="admin_user_id" label="操作人ID" width="100" />
          <el-table-column prop="action" label="操作" width="160" />
          <el-table-column prop="target_type" label="目标类型" width="120" />
          <el-table-column prop="detail" label="详情" min-width="250" />
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>
        <el-pagination v-model:current-page="auditPage" :page-size="50" :total="auditTotal" layout="prev, pager, next, total" @current-change="loadAudit" style="margin-top:16px;justify-content:flex-end" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getSystemConfig, updateSystemConfig, getRoles, getIpWhitelist, updateIpWhitelist, getSystemAuditLog } from '../../api/admin/system'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

// Config
const configRows = ref([]), configLoading = ref(false)
async function loadConfig() { configLoading.value = true; try { const { data } = await getSystemConfig(); configRows.value = data.items } finally { configLoading.value = false } }
async function saveConfig() {
  await updateSystemConfig(configRows.value.map(r => ({ key: r.key, value: r.value, description: r.description })))
  ElMessage.success('配置已保存')
}

// Roles
const roles = ref([]), rolesLoading = ref(false)
async function loadRoles() { rolesLoading.value = true; try { const { data } = await getRoles(); roles.value = data.items } finally { rolesLoading.value = false } }

// IP Whitelist
const ipEnabled = ref(false), ipListText = ref(''), ipLoading = ref(false)
async function loadIp() { ipLoading.value = true; try { const { data } = await getIpWhitelist(); ipEnabled.value = data.enabled; ipListText.value = (data.ips || []).join('\n') } finally { ipLoading.value = false } }
async function saveIpWhitelist() {
  await updateIpWhitelist({ enabled: ipEnabled.value, ips: ipListText.value.split('\n').filter(s => s.trim()) })
  ElMessage.success('IP白名单已更新')
}

// Free Usage Config
const usageUnlimited = ref(false), usageDailyLimit = ref(2), usageLoading = ref(false), usageSaving = ref(false)
async function loadUsageConfig() {
  usageLoading.value = true
  try {
    const { data } = await getSystemConfig()
    const map = {}
    data.items.forEach(c => { map[c.key] = c.value })
    usageUnlimited.value = map.free_usage_unlimited === 'true'
    usageDailyLimit.value = parseInt(map.free_usage_daily_limit || '2')
  } finally { usageLoading.value = false }
}
async function saveUsageConfig() {
  usageSaving.value = true
  try {
    await updateSystemConfig([
      { key: 'free_usage_unlimited', value: String(usageUnlimited.value), description: '免费使用不限次数开关' },
      { key: 'free_usage_daily_limit', value: String(usageDailyLimit.value), description: '每日免费使用次数上限' },
    ])
    ElMessage.success('免费额度配置已保存，立即生效')
  } finally { usageSaving.value = false }
}

// Audit
const auditLogs = ref([]), auditLoading = ref(false), auditPage = ref(1), auditTotal = ref(0)
async function loadAudit() {
  auditLoading.value = true
  try { const { data } = await getSystemAuditLog({ page: auditPage.value, size: 50 }); auditLogs.value = data.items; auditTotal.value = data.total } finally { auditLoading.value = false }
}

onMounted(() => { loadUsageConfig(); loadConfig(); loadRoles(); loadIp(); loadAudit() })
</script>
