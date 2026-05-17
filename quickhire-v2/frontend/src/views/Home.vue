<template>
  <div class="home">
    <NavBar />
    <main class="main-content">
      <h1 class="brand-hero">让你的简历脱颖而出</h1>
      <p class="brand-subtitle">AI 驱动的简历优化工具 — 粘贴简历，一键润色，生成专属面试题库</p>

      <div class="cta-row">
        <el-button type="primary" size="large" @click="$router.push('/resume-optimizer')">
          开始优化简历
        </el-button>
        <el-button size="large" @click="$router.push('/resume-optimizer')">
          快速演示 · 1 分钟体验
        </el-button>
      </div>

      <div class="social-proof">
        <div class="social-stat">
          <div class="num">10,000+</div>
          <div class="label">简历已优化</div>
        </div>
        <div class="social-stat">
          <div class="num">50,000+</div>
          <div class="label">面试题已生成</div>
        </div>
        <div class="social-stat">
          <div class="num">4.9/5</div>
          <div class="label">用户好评</div>
        </div>
      </div>

      <div class="step-preview">
        <span class="step"><span class="step-num">1</span> 粘贴/上传简历</span>
        <span class="arrow">→</span>
        <span class="step"><span class="step-num">2</span> AI 智能优化</span>
        <span class="arrow">→</span>
        <span class="step"><span class="step-num">3</span> 生成面试题库</span>
      </div>

      <h2 class="section-title">为什么选择快克简历优化</h2>
      <div class="feature-grid">
        <div class="feature-card" v-for="f in features" :key="f.title">
          <div class="fc-icon">{{ f.icon }}</div>
          <div class="fc-title">{{ f.title }}</div>
          <div class="fc-desc">{{ f.desc }}</div>
        </div>
      </div>

      <footer class="footer-line">Powered by FastAPI & Vue 3 & DeepSeek</footer>
    </main>
  </div>
</template>

<script setup>
import NavBar from '../components/layout/NavBar.vue'

const features = [
  { icon: '📝', title: '智能润色', desc: 'STAR 法则重写经历，数据量化成果，3 秒抓住 HR 眼球' },
  { icon: '🔍', title: '深度解析', desc: '自动提取技术栈、项目经验、技能关键词与薄弱点' },
  { icon: '📊', title: '多维评分', desc: '完整度 / 关键词 / 量化 / 结构 / 语言 六大维度诊断' },
  { icon: '📋', title: '专属题库', desc: '基于真实简历内容，千人千题，附带标准答案与话术' },
]
</script>

<style scoped>
.home { min-height: 100vh; background: linear-gradient(180deg, #f0fdfa 0%, #ecfdf5 100%); }
.main-content { padding: 80px 2rem 2rem; max-width: 960px; margin: 0 auto; }
.brand-hero { font-size: 2.5rem; font-weight: 700; color: #0f766e; text-align: center; margin-bottom: 0.75rem; }
.brand-subtitle { font-size: 1.1rem; color: #0d9488; text-align: center; margin-bottom: 2.5rem; }
.cta-row { display: flex; gap: 1rem; justify-content: center; margin-bottom: 2rem; }
.social-proof { display: flex; gap: 2rem; justify-content: center; margin: 2rem 0; }
.social-stat { text-align: center; }
.social-stat .num { font-size: 1.6rem; font-weight: 700; color: #0f766e; }
.social-stat .label { font-size: 0.78rem; color: #5b8a87; }
.step-preview { display: flex; gap: 1rem; justify-content: center; margin: 2rem 0; align-items: center; }
.step { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #5b8a87; }
.step-num { width: 32px; height: 32px; border-radius: 50%; background: #f0fdfa; border: 2px solid #ccfbf1; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; color: #0f766e; }
.arrow { color: #ccfbf1; }
.section-title { font-size: 1.25rem; font-weight: 600; color: #0f766e; text-align: center; margin: 2rem 0 1.25rem; }
.feature-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.feature-card { background: #fff; border-radius: 10px; padding: 1.5rem 1.25rem; border: 1px solid #ccfbf1; text-align: center; }
.fc-icon { font-size: 1.75rem; margin-bottom: 0.75rem; }
.fc-title { font-weight: 600; font-size: 0.95rem; color: #0f766e; margin-bottom: 0.35rem; }
.fc-desc { font-size: 0.82rem; color: #64748b; line-height: 1.5; }
.footer-line { margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid #ccfbf1; text-align: center; color: #5b8a87; font-size: 0.8rem; }
@media (max-width: 768px) { .feature-grid { grid-template-columns: repeat(2, 1fr); } .brand-hero { font-size: 1.8rem; } }
</style>
