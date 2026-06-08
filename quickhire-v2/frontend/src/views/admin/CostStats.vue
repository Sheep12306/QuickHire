<template>
  <div>
    <div class="page-header"><h2>成本统计</h2><p>AI API 调用成本分析</p></div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="8" v-for="s in stats" :key="s.label">
        <div class="stat-card">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value" style="font-size:22px">{{ s.value }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <div class="detail-card"><h3>每日成本趋势</h3>
          <v-chart :option="dailyChartOption" style="height:300px" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="detail-card"><h3>按模型统计</h3>
          <el-table :data="modelStats" stripe>
            <el-table-column prop="model" label="模型" />
            <el-table-column prop="calls" label="调用次数" />
            <el-table-column label="成本"><template #default="{ row }">${{ row.cost?.toFixed(6) }}</template></el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCostStats } from '../../api/admin/logs'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const stats = ref([{ label: '总成本', value: '$0' }, { label: '总调用', value: '0' }, { label: '总Tokens', value: '0' }])
const modelStats = ref([])
const dailyChartOption = reactive({
  tooltip: { trigger: 'axis' },
  grid: { left: 60, right: 20, top: 10, bottom: 20 },
  xAxis: { type: 'category', data: [], axisLabel: { fontSize: 10 } },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [], itemStyle: { color: '#409eff' } }],
})

onMounted(async () => {
  const { data } = await getCostStats(30)
  stats.value = [
    { label: '总成本', value: `$${data.total_cost?.toFixed(4)}` },
    { label: '总调用', value: data.total_calls?.toLocaleString() },
    { label: '总Tokens', value: data.total_tokens?.toLocaleString() },
  ]
  modelStats.value = data.by_model || []
  dailyChartOption.xAxis.data = (data.daily || []).map(d => d.date.slice(5))
  dailyChartOption.series[0].data = (data.daily || []).map(d => d.cost)
})
</script>
