<template>
  <div class="analytics-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">
        <el-icon style="margin-right:8px"><TrendCharts /></el-icon>
        数据分析看板
      </h1>

      <el-row :gutter="16" class="metric-row">
        <el-col :xs="12" :sm="12" :md="6" v-for="m in metrics" :key="m.label">
          <div class="metric-card card">
            <div class="metric-icon">
              <el-icon :size="20"><component :is="m.icon" /></el-icon>
            </div>
            <div class="metric-value">{{ m.value }}</div>
            <div class="metric-label">{{ m.label }}</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :xs="24" :md="12">
          <div class="chart-card card">
            <h3>
              <el-icon style="margin-right:4px"><Document /></el-icon>
              简历优化历程
            </h3>
            <div v-if="dashboard?.resume_timeline?.length" ref="timelineChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="chart-card card">
            <h3>
              <el-icon style="margin-right:4px"><Aim /></el-icon>
              技能维度雷达
            </h3>
            <div v-if="dashboard?.radar_data && Object.keys(dashboard.radar_data).length" ref="radarChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:1rem">
        <el-col :xs="24" :md="12">
          <div class="chart-card card">
            <h3>
              <el-icon style="margin-right:4px"><Microphone /></el-icon>
              面试得分趋势
            </h3>
            <div v-if="dashboard?.interview_scores?.length" ref="scoreChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="chart-card card">
            <h3>
              <el-icon style="margin-right:4px"><DataAnalysis /></el-icon>
              求职进度漏斗
            </h3>
            <div v-if="funnelData.length" ref="funnelChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
      </el-row>

      <div class="chart-card card" style="margin-top:1rem">
        <h3>添加求职记录</h3>
        <el-form inline>
          <el-form-item><el-input v-model="appForm.company_name" placeholder="公司名称" /></el-form-item>
          <el-form-item><el-input v-model="appForm.position" placeholder="职位" /></el-form-item>
          <el-form-item>
            <el-select v-model="appForm.status" style="width:120px">
              <el-option label="已投递" value="applied" />
              <el-option label="面试中" value="interview" />
              <el-option label="已Offer" value="offer" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item><el-button type="primary" @click="handleAddApp">添加</el-button></el-form-item>
        </el-form>
        <el-table :data="applications" style="margin-top:1rem" v-if="applications.length">
          <el-table-column prop="company_name" label="公司" />
          <el-table-column prop="position" label="职位" />
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="applied_at" label="投递时间" />
        </el-table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'
import * as echarts from 'echarts'
import { getDashboard, addApplication, getApplications } from '../api/analytics'
import NavBar from '../components/layout/NavBar.vue'

const dashboard = ref(null)
const applications = ref([])
const appForm = reactive({ company_name: '', position: '', status: 'applied' })

const timelineChart = ref(null)
const radarChart = ref(null)
const scoreChart = ref(null)
const funnelChart = ref(null)

const metrics = computed(() => {
  const d = dashboard.value || {}
  return [
    { label: '简历版本', value: d.resume_timeline?.length || 0, icon: 'Document' },
    { label: '面试次数', value: d.interview_scores?.length || 0, icon: 'Microphone' },
    { label: '投递总数', value: d.application_funnel?.total || 0, icon: 'UploadFilled' },
    { label: 'Offer率', value: (d.application_funnel?.offer_rate || 0) + '%', icon: 'Star' },
  ]
})

const funnelData = computed(() => {
  const sc = dashboard.value?.application_funnel?.status_counts || {}
  const stages = ['applied', 'interview', 'offer', 'accepted']
  const labels = { applied: '已投递', interview: '面试', offer: 'Offer', accepted: '已接受' }
  return stages.filter(s => sc[s]).map(s => ({ name: labels[s], value: sc[s] }))
})

async function loadData() {
  try {
    const { data } = await getDashboard()
    dashboard.value = data
    await loadApplications()
    await nextTick()
    renderCharts()
  } catch { /* handled */ }
}

async function loadApplications() {
  try {
    const { data } = await getApplications()
    applications.value = data
  } catch { /* handled */ }
}

async function handleAddApp() {
  if (!appForm.company_name || !appForm.position) return
  await addApplication({ ...appForm })
  appForm.company_name = ''
  appForm.position = ''
  await loadApplications()
  await loadData()
}

function renderCharts() {
  const d = dashboard.value
  if (!d) return

  if (timelineChart.value && d.resume_timeline?.length) {
    const chart = echarts.init(timelineChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 20, right: 20, bottom: 30, left: 40 },
      xAxis: { type: 'category', data: d.resume_timeline.map(t => `V${t.version}`) },
      yAxis: { type: 'value', max: 100 },
      series: [{
        name: '评分', type: 'line',
        data: d.resume_timeline.map(t => t.score || 0),
        smooth: true,
        lineStyle: { color: '#059669', width: 3 },
        itemStyle: { color: '#059669' },
        areaStyle: { color: 'rgba(5,150,105,0.08)' },
      }],
    })
  }

  if (radarChart.value && d.radar_data) {
    const chart = echarts.init(radarChart.value)
    const indicators = Object.keys(d.radar_data).map(k => ({ name: k, max: 100 }))
    const values = Object.values(d.radar_data)
    chart.setOption({
      radar: {
        indicator: indicators,
        shape: 'circle',
        axisName: { color: '#6b7280' },
      },
      series: [{
        type: 'radar',
        data: [{ value: values, name: '技能维度' }],
        itemStyle: { color: '#059669' },
        areaStyle: { color: 'rgba(5,150,105,0.15)' },
        lineStyle: { color: '#059669' },
      }],
    })
  }

  if (scoreChart.value && d.interview_scores?.length) {
    const chart = echarts.init(scoreChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 20, right: 20, bottom: 30, left: 40 },
      xAxis: { type: 'category', data: d.interview_scores.map((s, i) => `#${i + 1}`) },
      yAxis: { type: 'value', max: 100 },
      series: [{
        name: '得分', type: 'line',
        data: d.interview_scores.map(s => s.score || 0),
        smooth: true,
        lineStyle: { color: '#10b981', width: 3 },
        itemStyle: { color: '#10b981' },
        areaStyle: { color: 'rgba(16,185,129,0.08)' },
      }],
    })
  }

  if (funnelChart.value && funnelData.value.length) {
    const chart = echarts.init(funnelChart.value)
    const funnelColors = ['#059669', '#10b981', '#34d399', '#6ee7b7']
    chart.setOption({
      series: [{
        type: 'funnel',
        data: funnelData.value.map((f, i) => ({
          name: f.name, value: f.value,
          itemStyle: { color: funnelColors[i] || '#059669' },
        })),
      }],
    })
  }
}

onMounted(loadData)
watch(dashboard, () => nextTick(renderCharts))
</script>

<style scoped>
.analytics-page { min-height: 100vh; background: var(--bg-page); }
.main-content { padding: 80px 1.5rem 2rem; max-width: 1100px; margin: 0 auto; }
.page-title {
  font-size: 1.7rem; color: var(--text-primary); margin-bottom: 1.5rem;
  display: flex; align-items: center; font-weight: 700;
}

.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
}

.metric-row { margin-bottom: 1rem; }
.metric-card {
  padding: 1.25rem; text-align: center;
  transition: transform var(--duration-normal) var(--ease-out),
              box-shadow var(--duration-normal) var(--ease-out);
}
.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-green);
}
.metric-icon {
  color: var(--green-600); margin-bottom: 0.5rem;
  opacity: 0.8;
}
.metric-value {
  font-size: 1.8rem; font-weight: 800; color: var(--green-700);
  letter-spacing: -0.02em;
}
.metric-label {
  font-size: 0.78rem; color: var(--text-muted);
  margin-top: 0.25rem; font-weight: 500;
}

.chart-card { padding: 1.5rem; }
.chart-card h3 {
  color: var(--text-primary); margin-bottom: 1rem;
  font-size: 0.95rem; font-weight: 700;
  display: flex; align-items: center;
}

@media (max-width: 768px) {
  .main-content { padding: 70px 1rem 1.5rem; }
  .page-title { font-size: 1.4rem; }

  .metric-card { padding: 1rem; }
  .metric-value { font-size: 1.4rem; }

  .chart-card { padding: 1rem; }
  .chart-card h3 { font-size: 0.88rem; }

  /* Make form inline stack on mobile */
  .chart-card :deep(.el-form--inline) {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }
  .chart-card :deep(.el-form--inline .el-form-item) {
    margin-right: 0;
  }
  .chart-card :deep(.el-form--inline .el-input),
  .chart-card :deep(.el-form--inline .el-select) {
    width: 100% !important;
  }
}

@media (max-width: 480px) {
  .metric-value { font-size: 1.1rem; }
  .metric-label { font-size: 0.7rem; }
}
</style>
