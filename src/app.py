import streamlit as st
from database import init_db
from auth_service import AuthService

# ── Database init ─────────────────────────────────────────────
init_db()

# ── Auth helper ───────────────────────────────────────────────
def require_auth():
    if not st.session_state.get("user_id"):
        st.warning("请先登录以使用此功能")
        st.page_link("pages/01_login.py", label="🔐 前往登录")
        st.stop()

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="快克简历优化",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design System CSS ────────────────────────────────────────
DESIGN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    html, body, .stMarkdown, .stText, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox div {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* Hide sidebar completely on home page */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }

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
    }

    .main [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F0FDFA 0%, #ECFDF5 100%);
    }

    /* Hide Streamlit header/toolbar/deploy */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="baseButton-header"] { display: none !important; }

    /* Push main content down to make room for fixed nav */
    .main [data-testid="stAppViewContainer"] {
        padding-top: 62px !important;
    }
    .main [data-testid="stAppViewBlockContainer"] {
        padding-top: 0 !important;
    }

    /* ── Fixed Top Nav Bar ── */
    .topnav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 2rem;
        height: 56px;
        background: rgba(240, 253, 250, 0.95);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(204, 251, 241, 0.6);
        box-shadow: 0 1px 8px rgba(15, 118, 110, 0.06);
    }
    .topnav-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F766E;
    }
    .topnav-actions {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .btn-login {
        background: transparent;
        border: 1.5px solid #0D9488;
        color: #0D9488;
        padding: 0.45rem 1.25rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
    }
    .btn-login:hover {
        background: #0D9488;
        color: #FFFFFF;
    }
    .btn-register {
        background: linear-gradient(135deg, #0D9488 0%, #059669 100%);
        border: none;
        color: #FFFFFF;
        padding: 0.45rem 1.25rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(13, 148, 136, 0.25);
    }
    .btn-register:hover {
        box-shadow: 0 4px 16px rgba(13, 148, 136, 0.4);
        transform: translateY(-1px);
    }
    .user-avatar {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.85rem;
        color: #0F766E;
        font-weight: 600;
    }

    /* ── Typography ── */
    .brand-hero {
        font-family: 'DM Sans', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F766E;
        letter-spacing: -0.025em;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    .brand-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.1rem;
        color: #0D9488;
        line-height: 1.7;
        margin-bottom: 2.5rem;
        text-align: center;
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
    .feature-card .fc-icon { font-size: 1.75rem; margin-bottom: 0.75rem; }
    .feature-card .fc-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: #0F766E;
        margin-bottom: 0.35rem;
    }
    .feature-card .fc-desc { font-size: 0.82rem; color: #64748B; line-height: 1.5; }

    /* ── CTA buttons ── */
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

    /* ── Social proof ── */
    .social-proof {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin: 2rem 0 1.5rem;
    }
    .social-stat { text-align: center; }
    .social-stat .num {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F766E;
    }
    .social-stat .label { font-size: 0.78rem; color: #5B8A87; }

    /* ── Step preview ── */
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
        width: 32px; height: 32px;
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
        .topnav { padding: 0.5rem 1rem; }
    }
</style>
"""

st.markdown(DESIGN_CSS, unsafe_allow_html=True)

# ── Top Nav Bar ──────────────────────────────────────────────
logged_in = AuthService.is_logged_in()
display_name = st.session_state.get("display_name", "用户")

st.markdown(f"""
<div class="topnav">
    <div class="topnav-brand">
        <span style="font-size:1.5rem;">📝</span>
        <span>快克简历优化</span>
    </div>
    <div class="topnav-actions">
        {f'<div class="user-avatar">👤 {display_name}</div>'
         if logged_in else
         f'<a href="/pages/01_login" target="_self" class="btn-login">🔐 登录</a>'
         f'<a href="/pages/01_login" target="_self" class="btn-register">📝 注册</a>'}
    </div>
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
st.markdown('<div class="footer-line">Powered by Streamlit & DeepSeek</div>', unsafe_allow_html=True)
