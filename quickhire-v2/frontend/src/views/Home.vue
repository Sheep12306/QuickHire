<template>
  <div class="home">
    <NavBar />

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-blob hero-blob--1"></div>
        <div class="hero-blob hero-blob--2"></div>
        <div class="hero-blob hero-blob--3"></div>
      </div>
      <div class="hero-content animate-fade-up">
        <h1 class="hero-title">
          让简历<span class="hero-highlight">脱颖而出</span>
        </h1>
        <p class="hero-subtitle">
          AI 驱动的智能简历优化平台 — 粘贴简历，一键润色，生成专属面试题库
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/resume-optimizer')">
            <el-icon style="margin-right:6px"><EditPen /></el-icon>
            开始优化
          </el-button>
          <el-button size="large" round @click="$router.push('/resume-optimizer')">
            <el-icon style="margin-right:6px"><VideoPlay /></el-icon>
            快速演示
          </el-button>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section class="stats-section">
      <div class="stats-row animate-fade-up animate-delay-1">
        <div class="stat-item" v-for="s in stats" :key="s.label">
          <div class="stat-num">{{ s.num }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="steps-section">
      <div class="container animate-fade-up animate-delay-2">
        <h2 class="section-title">三步完成优化</h2>
        <div class="steps-row">
          <div class="step-item" v-for="(s, i) in steps" :key="s.title">
            <div class="step-icon-wrap">
              <el-icon class="step-icon"><component :is="s.icon" /></el-icon>
            </div>
            <div class="step-title">{{ s.title }}</div>
            <div class="step-desc">{{ s.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">全方位提升求职竞争力</h2>
        <div class="feature-grid">
          <div class="feature-card" v-for="f in features" :key="f.title">
            <div class="fc-icon-wrap">
              <el-icon class="fc-icon"><component :is="f.icon" /></el-icon>
            </div>
            <div class="fc-title">{{ f.title }}</div>
            <div class="fc-desc">{{ f.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <p class="footer-text">Powered by FastAPI & Vue 3 & DeepSeek</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import NavBar from '../components/layout/NavBar.vue'

const stats = [
  { num: '10,000+', label: '简历已优化' },
  { num: '50,000+', label: '面试题生成' },
  { num: '4.9 / 5', label: '用户好评' },
]

const steps = [
  { icon: 'Upload', title: '上传简历', desc: '粘贴文本或上传文件，自动解析' },
  { icon: 'MagicStick', title: 'AI 智能优化', desc: 'STAR 法则重写，数据量化成果' },
  { icon: 'Collection', title: '生成题库', desc: '千人千题，附带标准答案' },
]

const features = [
  { icon: 'Document', title: '智能润色', desc: 'STAR 法则重写经历，数据量化成果，3 秒抓住 HR 眼球' },
  { icon: 'Search', title: '深度解析', desc: '自动提取技术栈、项目经验、技能关键词与薄弱点' },
  { icon: 'DataAnalysis', title: '多维评分', desc: '完整度 / 关键词 / 量化 / 结构 / 语言六大维度诊断' },
  { icon: 'Notebook', title: '专属题库', desc: '基于真实简历内容，个性化出题，附带标准答案与话术' },
]
</script>

<style scoped>
/* ── Layout ─────────────────────────────── */
.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* ── Hero ───────────────────────────────── */
.hero {
  position: relative;
  padding: 140px 1.5rem 80px;
  text-align: center;
  overflow: hidden;
}
.hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}
.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}
.hero-blob--1 {
  width: 400px; height: 400px;
  top: -100px; right: -100px;
  background: var(--green-200);
}
.hero-blob--2 {
  width: 300px; height: 300px;
  bottom: -60px; left: -60px;
  background: var(--green-100);
}
.hero-blob--3 {
  width: 200px; height: 200px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: var(--green-300);
  opacity: 0.2;
}
.hero-content {
  position: relative;
  z-index: 1;
}
.hero-title {
  font-size: clamp(2.5rem, 5vw, 3.75rem);
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.15;
  margin: 0 0 1.25rem;
  letter-spacing: -0.03em;
}
.hero-highlight {
  background: linear-gradient(135deg, var(--green-600), var(--green-500));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-subtitle {
  font-size: 1.15rem;
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto 2.5rem;
  line-height: 1.6;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* ── Stats ──────────────────────────────── */
.stats-section {
  padding: 0 1.5rem 3rem;
}
.stats-row {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  padding: 1.5rem;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}
.stat-item {
  text-align: center;
}
.stat-num {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--green-700);
  letter-spacing: -0.02em;
}
.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
  font-weight: 500;
}

/* ── Steps ──────────────────────────────── */
.steps-section {
  padding: 3rem 0;
}
.section-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin: 0 0 2.5rem;
  letter-spacing: -0.02em;
}
.steps-row {
  display: flex;
  justify-content: center;
  gap: 2rem;
  position: relative;
}
.steps-row::before {
  content: '';
  position: absolute;
  top: 36px;
  left: calc(16.6% + 30px);
  right: calc(16.6% + 30px);
  height: 2px;
  background: linear-gradient(90deg, var(--green-300), var(--green-500), var(--green-300));
  border-radius: 2px;
}
.step-item {
  flex: 1;
  max-width: 200px;
  text-align: center;
  position: relative;
  z-index: 1;
}
.step-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--bg-surface);
  border: 2px solid var(--green-200);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  box-shadow: var(--shadow-sm);
  transition: transform var(--duration-normal) var(--ease-out),
              box-shadow var(--duration-normal) var(--ease-out);
}
.step-item:hover .step-icon-wrap {
  transform: translateY(-4px);
  box-shadow: var(--shadow-green);
}
.step-icon {
  font-size: 1.6rem;
  color: var(--green-600);
}
.step-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  margin-bottom: 0.35rem;
}
.step-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* ── Features ───────────────────────────── */
.features-section {
  padding: 3rem 0 4rem;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}
.feature-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 1.75rem 1.5rem;
  border: 1px solid var(--border-light);
  text-align: center;
  box-shadow: var(--shadow-xs);
  transition: transform var(--duration-normal) var(--ease-out),
              box-shadow var(--duration-normal) var(--ease-out);
  position: relative;
  overflow: hidden;
}
.feature-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--green-400), var(--green-600));
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
}
.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-green);
}
.feature-card:hover::before {
  opacity: 1;
}
.fc-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--green-50);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}
.fc-icon {
  font-size: 1.5rem;
  color: var(--green-600);
}
.fc-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
}
.fc-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.55;
}

/* ── Footer ─────────────────────────────── */
.footer {
  padding: 2rem 0;
  text-align: center;
  border-top: 1px solid var(--border-light);
}
.footer-text {
  color: var(--text-muted);
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .hero { padding: 90px 1.25rem 40px; }
  .hero-title { font-size: clamp(1.6rem, 7vw, 2rem); margin-bottom: 0.75rem; }
  .hero-subtitle { font-size: 0.95rem; max-width: 100%; margin-bottom: 1.5rem; }
  .hero-actions { flex-direction: column; align-items: center; }
  .hero-actions .el-button { width: 100%; max-width: 320px; }
  .hero-blob--1 { width: 200px; height: 200px; }
  .hero-blob--2 { width: 150px; height: 150px; }

  .stats-section { padding: 0 1rem 1.5rem; }
  .stats-row { flex-wrap: wrap; gap: 0 1.5rem; padding: 1rem 0.75rem; }
  .stat-num { font-size: 1.25rem; }
  .stat-label { font-size: 0.72rem; }

  .section-title { font-size: 1.2rem; margin-bottom: 1.25rem; }
  .steps-section { padding: 1.5rem 0; }
  .steps-row { flex-direction: column; align-items: center; gap: 1rem; }
  .steps-row::before { display: none; }
  .step-item { max-width: 280px; }
  .step-icon-wrap { width: 52px; height: 52px; margin-bottom: 0.5rem; }
  .step-icon { font-size: 1.3rem; }
  .step-title { font-size: 0.9rem; }
  .step-desc { font-size: 0.78rem; }

  .features-section { padding: 1.5rem 0 2rem; }
  .feature-grid { grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  .feature-card { padding: 1rem 0.85rem; }
  .fc-icon-wrap { width: 40px; height: 40px; border-radius: 10px; margin-bottom: 0.5rem; }
  .fc-icon { font-size: 1.2rem; }
  .fc-title { font-size: 0.88rem; }
  .fc-desc { font-size: 0.76rem; }

  .container { padding: 0 1rem; }
  .footer { padding: 1.25rem 0; }
}

@media (max-width: 480px) {
  .hero { padding: 75px 1rem 32px; }
  .hero-title { font-size: 1.5rem; }
  .hero-subtitle { font-size: 0.85rem; }

  .stats-section { padding: 0 0.75rem 1rem; }
  .stats-row { gap: 0 0.75rem; padding: 0.75rem 0.5rem; }
  .stat-num { font-size: 1.05rem; }
  .stat-label { font-size: 0.68rem; }

  .feature-grid { grid-template-columns: 1fr; gap: 0.5rem; }
  .feature-card { padding: 0.85rem 0.75rem; }
  .fc-title { font-size: 0.85rem; }
  .fc-desc { font-size: 0.74rem; }

  .section-title { font-size: 1.1rem; margin-bottom: 1rem; }
}
</style>
