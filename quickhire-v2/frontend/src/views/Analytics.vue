<template>
  <div class="analytics-page">
    <NavBar />
    <main class="main-content">
      <h1 class="page-title">📊 数据分析看板</h1>

      <!-- Metric Cards -->
      <el-row :gutter="16" class="metric-row">
        <el-col :span="6" v-for="m in metrics" :key="m.label">
          <div class="metric-card">
            <div class="metric-value">{{ m.value }}</div>
            <div class="metric-label">{{ m.label }}</div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <!-- Resume Timeline -->
        <el-col :span="12">
          <div class="chart-card">
            <h3>简历优化历程</h3>
            <div v-if="dashboard?.resume_timeline?.length" ref="timelineChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>

        <!-- Skill Radar -->
        <el-col :span="12">
          <div class="chart-card">
            <h3>技能维度雷达</h3>
            <div v-if="dashboard?.radar_data && Object.keys(dashboard.radar_data).length" ref="radarChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:1rem">
        <!-- Interview Scores -->
        <el-col :span="12">
          <div class="chart-card">
            <h3>面试得分趋势</h3>
            <div v-if="dashboard?.interview_scores?.length" ref="scoreChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>

        <!-- Application Funnel -->
        <el-col :span="12">
          <div class="chart-card">
            <h3>求职进度漏斗</h3>
            <div v-if="funnelData.length" ref="funnelChart" style="height:300px"></div>
            <el-empty v-else description="暂无数据" />
          </div>
        </el-col>
      </el-row>

      <!-- Add Application -->
      <div class="chart-card" style="margin-top:1rem">
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
    { label: '简历版本', value: d.resume_timeline?.length || 0 },
    { label: '面试次数', value: d.interview_scores?.length || 0 },
    { label: '投递总数', value: d.application_funnel?.total || 0 },
    { label: 'Offer率', value: (d.application_funnel?.offer_rate || 0) + '%' },
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
  } catch { /* handled by interceptor */ }
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

  // Timeline line chart
  if (timelineChart.value && d.resume_timeline?.length) {
    const chart = echarts.init(timelineChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: d.resume_timeline.map(t => `V${t.version}`) },
      yAxis: { type: 'value', max: 100 },
      series: [{
        name: '评分', type: 'line',
        data: d.resume_timeline.map(t => t.score || 0),
        smooth: true,
        itemStyle: { color: '#0d9488' },
      }],
    })
  }

  // Radar chart
  if (radarChart.value && d.radar_data) {
    const chart = echarts.init(radarChart.value)
    const indicators = Object.keys(d.radar_data).map(k => ({ name: k, max: 100 }))
    const values = Object.values(d.radar_data)
    chart.setOption({
      radar: { indicator: indicators, shape: 'circle' },
      series: [{ type: 'radar', data: [{ value: values, name: '技能维度' }], itemStyle: { color: '#0d9488' } }],
    })
  }

  // Score line chart
  if (scoreChart.value && d.interview_scores?.length) {
    const chart = echarts.init(scoreChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: d.interview_scores.map((s, i) => `#${i + 1}`) },
      yAxis: { type: 'value', max: 100 },
      series: [{
        name: '得分', type: 'line',
        data: d.interview_scores.map(s => s.score || 0),
        smooth: true,
        itemStyle: { color: '#059669' },
      }],
    })
  }

  // Funnel chart
  if (funnelChart.value && funnelData.value.length) {
    const chart = echarts.init(funnelChart.value)
    chart.setOption({
      series: [{
        type: 'funnel',
        data: funnelData.value.map(f => ({ name: f.name, value: f.value })),
        itemStyle: { color: '#0d9488' },
      }],
    })
  }
}

onMounted(loadData)
watch(dashboard, () => nextTick(renderCharts))
</script>

<style scoped>
.analytics-page { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 1100px; margin: 0 auto; }
.page-title { font-size: 1.8rem; color: #0f766e; margin-bottom: 1.5rem; }
.metric-row { margin-bottom: 1rem; }
.metric-card { background: #fff; border-radius: 10px; padding: 1.5rem; text-align: center; border: 1px solid #ccfbf1; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #0f766e; }
.metric-label { font-size: 0.8rem; color: #5b8a87; margin-top: 0.25rem; }
.chart-card { background: #fff; border-radius: 12px; padding: 1.5rem; border: 1px solid #ccfbf1; }
.chart-card h3 { color: #0f766e; margin-bottom: 1rem; font-size: 1rem; }
</style>
