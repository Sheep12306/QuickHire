import streamlit as st

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="快克简历优化",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System CSS ────────────────────────────────────────
DESIGN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    html, body, .stMarkdown, .stText, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox div, [data-testid="stSidebar"] * {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    /* Material Icons elements: restore icon font to prevent ligature text leakage */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    button[data-testid="baseButton-header"],
    button[data-testid="baseButton-header"] *,
    .material-icons {
        font-family: 'Material Icons' !important;
    }

    :root {
        --teal-50:  #F0FDFA;
        --teal-100: #CCFBF1;
        --teal-200: #99F6E4;
        --teal-300: #5EEAD4;
        --teal-400: #2DD4BF;
        --teal-500: #14B8A6;
        --teal-600: #0D9488;
        --teal-700: #0F766E;
        --teal-800: #115E59;
        --teal-900: #134E4A;
        --emerald-500: #10B981;
        --emerald-600: #059669;
        --emerald-700: #047857;
        --cyan-500: #06B6D4;
        --cyan-600: #0891B2;
        --muted: #5B8A87;
        --stone-50: #FAFAF9;
        --stone-200: #E7E5E4;
        --stone-400: #A8A29E;
        --stone-500: #78716C;
        --stone-900: #1C1917;
    }

    /* ── Hide Streamlit auto-generated nav (using manual page_link instead) ── */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* ── Sidebar: 青→绿自然过渡 ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(175deg, #0A4C4E 0%, #0F766E 45%, #065F46 100%);
        border-right: none;
        box-shadow: 2px 0 24px rgba(10, 76, 78, 0.15);
    }
    [data-testid="stSidebar"] * {
        color: #CCFBF1 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(204, 251, 241, 0.12) !important;
    }
    [data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #CCFBF1 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(255,255,255,0.16) !important;
        border-color: rgba(255,255,255,0.25) !important;
    }

    /* ── Main area ── */
    .main [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F0FDFA 0%, #ECFDF5 100%);
    }

    /* ── Typography ── */
    .brand-hero {
        font-family: 'DM Sans', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F766E;
        letter-spacing: -0.025em;
        margin-bottom: 0.75rem;
    }
    .brand-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.1rem;
        color: #0D9488;
        line-height: 1.7;
        margin-bottom: 2.5rem;
    }
    .section-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #0F766E;
        margin-bottom: 1.25rem;
    }

    /* ── Feature cards ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2.5rem 0;
    }
    .feature-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem 1.25rem;
        border: 1px solid #CCFBF1;
        text-align: center;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
    }
    .feature-card:hover {
        border-color: #5EEAD4;
        box-shadow: 0 4px 20px rgba(15, 118, 110, 0.08);
        transform: translateY(-2px);
    }
    .feature-card .fc-icon {
        font-size: 1.75rem;
        margin-bottom: 0.75rem;
    }
    .feature-card .fc-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: #0F766E;
        margin-bottom: 0.35rem;
    }
    .feature-card .fc-desc {
        font-size: 0.82rem;
        color: #64748B;
        line-height: 1.5;
    }

    /* ── CTA button override ── */
    .st-key-hero_cta button {
        background: linear-gradient(135deg, #0D9488 0%, #059669 100%) !important;
        border: none !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 2.5rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .st-key-hero_cta button:hover {
        box-shadow: 0 6px 22px rgba(13, 148, 136, 0.4) !important;
        transform: translateY(-1px);
    }

    /* ── Footer ── */
    .footer-line {
        margin-top: 3rem;
        padding-top: 1.25rem;
        border-top: 1px solid #CCFBF1;
        text-align: center;
        color: #5B8A87;
        font-size: 0.8rem;
    }

    /* ── Focus ── */
    *:focus-visible {
        outline: 2px solid #14B8A6;
        outline-offset: 2px;
        border-radius: 4px;
    }

    @media (max-width: 768px) {
        .feature-grid { grid-template-columns: repeat(2, 1fr); }
        .brand-hero { font-size: 1.8rem; }
    }

    /* ── Social proof ── */
    .social-proof {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin: 2rem 0 1.5rem;
    }
    .social-stat {
        text-align: center;
    }
    .social-stat .num {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F766E;
    }
    .social-stat .label {
        font-size: 0.78rem;
        color: #5B8A87;
    }

    /* ── Demo button ── */
    .st-key-hero_demo button {
        background: #FFFFFF !important;
        border: 2px solid #99F6E4 !important;
        color: #0F766E !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 2.5rem !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    .st-key-hero_demo button:hover {
        border-color: #2DD4BF !important;
        background: #F0FDFA !important;
        transform: translateY(-1px);
    }

    /* ── Privacy badge (sidebar) ── */
    .privacy-badge {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 0.75rem;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        font-size: 0.7rem;
        color: #99C7C3;
        margin-top: 1rem;
    }

    /* ── Step preview mini ── */
    .step-preview {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    .step-preview-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #5B8A87;
    }
    .step-preview-num {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #F0FDFA;
        border: 2px solid #CCFBF1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        color: #0F766E;
    }
</style>
"""

st.markdown(DESIGN_CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="padding:0.5rem 0 1.5rem 0;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                <span style="font-size:1.5rem;">📝</span>
                <span style="font-size:1.15rem;font-weight:700;color:#FFFFFF;">快克简历优化</span>
            </div>
            <div style="font-size:0.78rem;color:#5EEAD4;">AI 简历优化 & 面试题生成</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.page_link("app.py", label="🏠 首页")
    st.page_link("pages/02_resume_optimizer.py", label="📝 简历优化中心")

    st.markdown("---")

    st.markdown("""
        <div style="font-size:0.75rem;color:#99C7C3;line-height:1.6;">
            <div style="font-weight:600;color:#99F6E4;margin-bottom:0.25rem;">核心功能</div>
            · 简历智能润色<br>
            · AI 深度分析<br>
            · 个性化面试题库<br>
        </div>
    """, unsafe_allow_html=True)

    # Privacy badge
    st.markdown("""
        <div class="privacy-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5EEAD4" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            上传内容仅用于分析，不保存或共享
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="font-size:0.72rem;color:#7AADA9;margin-top:1.5rem;line-height:1.5;">
            Powered by Streamlit<br>& 通义千问
        </div>
    """, unsafe_allow_html=True)

# ── Main Content ─────────────────────────────────────────────
st.markdown(
    '<div class="brand-hero">让你的简历脱颖而出</div>'
    '<div class="brand-subtitle">AI 驱动的简历优化工具 — 粘贴简历，一键润色，生成专属面试题库</div>',
    unsafe_allow_html=True
)

col_cta, col_demo, col_spacer = st.columns([2, 2, 1])
with col_cta:
    if st.button("开始优化简历", type="primary", key="hero_cta", use_container_width=True):
        st.switch_page("pages/02_resume_optimizer.py")
with col_demo:
    if st.button("快速演示 1 分钟体验", key="hero_demo", use_container_width=True):
        st.switch_page("pages/02_resume_optimizer.py")

# Social proof
st.markdown("""
    <div class="social-proof">
        <div class="social-stat"><div class="num">10,000+</div><div class="label">简历已优化</div></div>
        <div class="social-stat"><div class="num">50,000+</div><div class="label">面试题已生成</div></div>
        <div class="social-stat"><div class="num">4.9/5</div><div class="label">用户好评</div></div>
    </div>
""", unsafe_allow_html=True)

# Step preview
st.markdown("""
    <div class="step-preview">
        <div class="step-preview-item"><div class="step-preview-num">1</div> 粘贴/上传简历</div>
        <div style="color:#CCFBF1;">→</div>
        <div class="step-preview-item"><div class="step-preview-num">2</div> AI 智能优化</div>
        <div style="color:#CCFBF1;">→</div>
        <div class="step-preview-item"><div class="step-preview-num">3</div> 生成面试题库</div>
    </div>
""", unsafe_allow_html=True)

# Feature grid
st.markdown('<div class="section-title">为什么选择快克简历优化</div>', unsafe_allow_html=True)

st.markdown('<div class="feature-grid">', unsafe_allow_html=True)

features = [
    ("📝", "智能润色", "STAR 法则重写经历，数据量化成果，3 秒抓住 HR 眼球"),
    ("🔍", "深度解析", "自动提取技术栈、项目经验、技能关键词与薄弱点"),
    ("📊", "多维评分", "完整度 / 关键词 / 量化 / 结构 / 语言 六大维度诊断"),
    ("📋", "专属题库", "基于真实简历内容，千人千题，附带标准答案与话术"),
]

for icon, title, desc in features:
    st.markdown(
        f'<div class="feature-card">'
        f'<div class="fc-icon">{icon}</div>'
        f'<div class="fc-title">{title}</div>'
        f'<div class="fc-desc">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer-line">Powered by Streamlit & 通义千问</div>', unsafe_allow_html=True)
