<template>
  <div>
    <div class="page-header">
      <h2>管理仪表盘</h2>
      <p>系统运行概览与核心指标</p>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :xs="12" :sm="8" :lg="4" v-for="card in kpiCards" :key="card.label">
        <div class="stat-card">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="stat-sub">{{ card.sub }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="16">
        <div class="detail-card">
          <h3>
            近 {{ trendDays }} 天趋势
            <el-radio-group v-model="trendDays" size="small" style="float:right">
              <el-radio-button :value="7">7天</el-radio-button>
              <el-radio-button :value="30">30天</el-radio-button>
            </el-radio-group>
          </h3>
          <v-chart :option="trendChartOption" style="height:320px" autoresize />
        </div>
      </el-col>
      <el-col :span="8">
        <div class="detail-card">
          <h3>功能使用排行</h3>
          <v-chart :option="featureRankOption" style="height:320px" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <div class="detail-card">
          <h3>最近动态</h3>
          <div v-if="activities.length === 0" style="color:var(--el-text-color-placeholder);text-align:center;padding:40px">暂无数据</div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in activities"
              :key="item.time"
              :timestamp="item.time"
              placement="top"
              :type="item.type === 'user_registered' ? 'success' : 'primary'"
            >
              {{ item.message }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="detail-card">
          <h3>
            系统告警
            <el-tag v-if="alerts.length === 0" type="success" size="small" style="float:right">运行正常</el-tag>
          </h3>
          <div v-if="alerts.length === 0" style="color:var(--el-text-color-placeholder);text-align:center;padding:40px">当前无告警</div>
          <div v-else>
            <div v-for="a in alerts" :key="a.message" class="alert-item" style="padding:10px 0;border-bottom:1px solid var(--el-border-color-light)">
              <el-tag :type="a.level === 'error' ? 'danger' : a.level === 'warning' ? 'warning' : 'info'" size="small" effect="dark">
                {{ a.level === 'error' ? '严重' : a.level === 'warning' ? '警告' : '提示' }}
              </el-tag>
              <span style="margin-left:8px">{{ a.message }}</span>
              <span style="float:right;font-size:12px;color:var(--el-text-color-placeholder)">{{ a.time }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getDashboardOverview, getTrends, getAlerts, getFeatureRanking, getRecentActivities } from '../../api/admin/dashboard'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

const kpiCards = ref([
  { label: '总用户数', value: '-', sub: '', color: '#059669' },
  { label: '今日新增', value: '-', sub: '', color: '#10b981' },
  { label: '7日活跃', value: '-', sub: '', color: '#047857' },
  { label: '总简历数', value: '-', sub: '', color: '#059669' },
  { label: '今日优化', value: '-', sub: '', color: '#10b981' },
  { label: '错误率', value: '-', sub: '', color: '#10b981' },
])

const trendDays = ref(7)
const trendData = ref([])
const featureRanking = ref([])
const alerts = ref([])
const activities = ref([])

const trendChartOption = reactive({
  tooltip: { trigger: 'axis' },
  legend: { data: ['注册', '优化', 'API调用'], bottom: 0 },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: [], axisLabel: { rotate: 30, fontSize: 10 } },
  yAxis: { type: 'value' },
  color: ['#059669', '#10b981', '#34d399'],
  series: [
    { name: '注册', type: 'line', data: [], smooth: true, lineStyle: { width: 2 } },
    { name: '优化', type: 'line', data: [], smooth: true, lineStyle: { width: 2 } },
    { name: 'API调用', type: 'line', data: [], smooth: true, lineStyle: { width: 2 } },
  ],
})

const featureRankOption = reactive({
  tooltip: { trigger: 'item' },
  color: ['#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#047857', '#065f46', '#064e3b', '#d1fae5', '#ecfdf5'],
  series: [{
    type: 'pie',
    radius: ['45%', '75%'],
    center: ['50%', '50%'],
    label: { formatter: '{b}\n{d}%' },
    data: [],
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
  }],
})

async function loadData() {
  try {
    const [overviewRes, trendsRes, alertsRes, rankingRes, activitiesRes] = await Promise.all([
      getDashboardOverview(),
      getTrends(trendDays.value),
      getAlerts(),
      getFeatureRanking(30),
      getRecentActivities(15),
    ])

    const o = overviewRes.data
    kpiCards.value = [
      { label: '总用户数', value: o.total_users?.toLocaleString() || '0', sub: '', color: '#059669' },
      { label: '今日新增', value: o.new_users_today || '0', sub: '', color: '#10b981' },
      { label: '7日活跃', value: o.active_users_7d || '0', sub: '', color: '#047857' },
      { label: '总简历数', value: o.total_resumes?.toLocaleString() || '0', sub: `优化 ${o.total_optimizations?.toLocaleString() || 0} 次`, color: '#059669' },
      { label: '今日优化', value: o.optimizations_today || '0', sub: `AI调用 ${o.ai_calls_today || 0} 次`, color: '#10b981' },
      { label: '错误率', value: `${o.error_rate || 0}%`, sub: '', color: o.error_rate > 10 ? '#ef4444' : '#10b981' },
    ]

    trendData.value = trendsRes.data.items || []
    updateTrendChart()

    alerts.value = alertsRes.data.items || []
    activities.value = activitiesRes.data.items || []

    const ranking = rankingRes.data.items || []
    featureRankOption.series[0].data = ranking.map(r => ({ name: r.name, value: r.count }))
  } catch {
    // silently fail, will show empty state
  }
}

function updateTrendChart() {
  const data = trendData.value
  trendChartOption.xAxis.data = data.map(d => d.date.slice(5))
  trendChartOption.series[0].data = data.map(d => d.registrations)
  trendChartOption.series[1].data = data.map(d => d.optimizations)
  trendChartOption.series[2].data = data.map(d => d.api_calls)
}

watch(trendDays, async () => {
  try {
    const { data } = await getTrends(trendDays.value)
    trendData.value = data.items || []
    updateTrendChart()
  } catch {}
})

onMounted(loadData)
</script>
