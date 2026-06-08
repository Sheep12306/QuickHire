<template>
  <div>
    <div class="page-header"><h2>运营分析</h2><p>用户转化漏斗与留存数据</p></div>

    <!-- Conversion Funnel -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="12">
        <div class="detail-card"><h3>转化漏斗</h3>
          <v-chart :option="funnelOption" style="height:300px" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="detail-card"><h3>用户留存</h3>
          <el-table :data="retention" stripe>
            <el-table-column prop="cohort" label="队列" width="120" />
            <el-table-column prop="size" label="人数" width="80" />
            <el-table-column label="次日留存"><template #default="{ row }">{{ row.day1 }}%</template></el-table-column>
            <el-table-column label="7日留存"><template #default="{ row }">{{ row.day7 }}%</template></el-table-column>
            <el-table-column label="30日留存"><template #default="{ row }">{{ row.day30 }}%</template></el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- Feature Heatmap -->
    <div class="detail-card">
      <h3>功能使用热力图（近30天）</h3>
      <div v-if="heatmapData.length === 0" style="text-align:center;color:var(--el-text-color-placeholder);padding:40px">暂无数据</div>
      <v-chart v-else :option="heatmapOption" style="height:300px" autoresize />
    </div>

    <!-- Export -->
    <div style="margin-top:16px">
      <el-button type="primary" @click="handleExport">导出报表 (CSV)</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getConversionFunnel, getRetention, getFeatureUsageHeatmap, exportReport } from '../../api/admin/analytics'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { HeatmapChart } from 'echarts/charts'
use([CanvasRenderer, BarChart, HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent])

const funnelData = ref({})
const retention = ref([])
const heatmapData = ref([])

const funnelOption = reactive({
  tooltip: { trigger: 'axis' },
  grid: { left: 80, right: 20, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: ['注册', '上传简历', '完成优化', '模拟面试', '投递记录'],
  },
  series: [{ type: 'bar', data: [], itemStyle: { color: '#409eff' }, label: { show: true, position: 'right' } }],
})

const heatmapOption = reactive({
  tooltip: { position: 'top' },
  grid: { left: 60, right: 20, top: 10, bottom: 40 },
  xAxis: { type: 'category', data: [], splitArea: { show: true } },
  yAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}时`), splitArea: { show: true } },
  visualMap: { min: 0, max: 10, calculable: true, orient: 'horizontal', left: 'center', bottom: 0 },
  series: [{ type: 'heatmap', data: [], label: { show: false }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,.5)' } } }],
})

onMounted(async () => {
  const [funnelRes, retRes, heatRes] = await Promise.all([getConversionFunnel(), getRetention(), getFeatureUsageHeatmap()])
  funnelData.value = funnelRes.data
  funnelOption.series[0].data = [funnelRes.data.registered, funnelRes.data.uploaded_resume, funnelRes.data.optimized, funnelRes.data.interviewed, funnelRes.data.applied]
  retention.value = retRes.data.items || []
  heatmapData.value = heatRes.data.items || []

  if (heatmapData.value.length > 0) {
    const dates = [...new Set(heatmapData.value.map(d => d[0]))].sort()
    heatmapOption.xAxis.data = dates.map(d => d.slice(5))
    heatmapOption.series[0].data = heatmapData.value.map(d => [dates.indexOf(d[0]), d[1], d[2]])
    heatmapOption.visualMap.max = Math.max(...heatmapData.value.map(d => d[2]), 1)
  }
})

async function handleExport() {
  const { data } = await exportReport(['users', 'resumes', 'api_calls'])
  const blob = new Blob([data], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `report_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
}
</script>
