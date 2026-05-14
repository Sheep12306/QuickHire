import streamlit as st
import json
import os

os.chdir(os.path.dirname(os.path.dirname(__file__)))

from api_client import call_qwen_api_with_retry
from prompt_builder import build_optimize_prompt, build_interview_question_prompt, build_resume_diagnosis_prompt
from file_parser import parse_uploaded_file, get_supported_formats
from resume_parser import parse_resume_text, resume_to_summary
from defect_detector import ResumeDefectDetector

st.set_page_config(
    page_title="简历优化中心 - 快克简历优化",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ────────────────────────────────────────────────
OPTIMIZATION_STYLES = ["简洁专业", "突出业绩", "技术导向", "创新风格"]
INTERVIEW_DIFFICULTIES = ["入门", "基础", "中等", "面试高频", "深度深挖"]
INTERVIEW_QUESTION_TYPES = ["选择题", "简答题", "项目手撕题", "场景面试题", "压力面试题"]
INTERVIEW_SCOPES = ["仅技术面试", "仅HR面试", "全题型混合"]

# ── Design System CSS ────────────────────────────────────────
STYLE_CSS = """
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
    .material-icons,
    span[data-testid="stMarkdown"] span {
        font-family: 'Material Icons' !important;
    }

    /* ── Hide Streamlit auto-generated nav (using manual page_link instead) ── */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Sidebar — deep teal gradient, 青→绿过渡 */
    [data-testid="stSidebar"] {
        background: linear-gradient(175deg, #0A4C4E 0%, #0F766E 45%, #065F46 100%);
        border-right: none;
        box-shadow: 2px 0 24px rgba(10, 76, 78, 0.15);
    }
    [data-testid="stSidebar"] * { color: #CCFBF1 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
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
    [data-testid="stSidebar"] hr { border-color: rgba(204, 251, 241, 0.12) !important; }

    /* Main area background — 青绿极淡渐变 */
    .main [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F0FDFA 0%, #ECFDF5 100%);
    }

    /* Typography */
    .page-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F766E;
        letter-spacing: -0.01em;
    }

    /* Cards */
    .card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #CCFBF1;
    }
    .card-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #0F766E;
        margin-bottom: 1rem;
    }

    /* Score badges */
    .score-badge {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'DM Sans', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 auto;
        color: white;
    }
    .score-s { background: linear-gradient(135deg, #0D9488, #10B981); }
    .score-a { background: linear-gradient(135deg, #0891B2, #06B6D4); }
    .score-b { background: linear-gradient(135deg, #D97706, #F59E0B); }
    .score-c { background: linear-gradient(135deg, #DC2626, #EF4444); }
    .score-d { background: linear-gradient(135deg, #6B7280, #9CA3AF); }

    /* Progress bars */
    .progress-bar-bg {
        height: 6px;
        background: #CCFBF1;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.25rem;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 0;
        color: #5B8A87;
    }
    .empty-state p {
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }

    /* Shared input section */
    .shared-input-section {
        background: #FFFFFF;
        border: 1px solid #CCFBF1;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    /* Defect badges */
    .quick-scan-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .badge-high { background: #FEE2E2; color: #991B1B; }
    .badge-medium { background: #FEF3C7; color: #92400E; }
    .badge-low { background: #CCFBF1; color: #0F766E; }

    /* Focus */
    *:focus-visible {
        outline: 2px solid #14B8A6;
        outline-offset: 2px;
        border-radius: 4px;
    }

    /* Streamlit tab overrides */
    .stTabs [data-baseweb="tab"] {
        color: #0F766E !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0D9488 !important;
    }

    /* ── Step progress indicator ── */
    .step-indicator {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        padding: 0.5rem 0;
    }
    .step-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .step-circle {
        width: 28px;
        height: 28px;
        min-width: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 600;
        background: rgba(255,255,255,0.12);
        color: #99F6E4;
        transition: all 0.3s ease;
    }
    .step-circle.active {
        background: #14B8A6;
        color: #FFFFFF;
        box-shadow: 0 0 12px rgba(20, 184, 166, 0.4);
    }
    .step-circle.done {
        background: #5EEAD4;
        color: #0F766E;
    }
    .step-label {
        font-size: 0.78rem;
        color: #99C7C3;
    }
    .step-label.active {
        color: #5EEAD4;
        font-weight: 600;
    }

    /* ── Pulse animation ── */
    @keyframes pulse-teal {
        0%, 100% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(20, 184, 166, 0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .animate-in {
        animation: fadeInUp 0.4s ease forwards;
    }
    .pulse-ring {
        animation: pulse-teal 2s infinite;
    }

    /* ── Upload area enhancement ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #99F6E4 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        background: #F0FDFA !important;
        transition: border-color 0.2s ease, background 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #2DD4BF !important;
        background: #E6FEFA !important;
    }

    /* ── Tab description ── */
    .tab-desc-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        margin-top: -0.5rem;
    }
    .tab-desc-chip {
        flex: 1;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        font-size: 0.75rem;
        color: #5B8A87;
        background: #F0FDFA;
        border: 1px solid #CCFBF1;
        line-height: 1.4;
    }
    .tab-desc-chip span {
        font-weight: 600;
        color: #0F766E;
    }

    /* ── Privacy badge ── */
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

    /* ── Diff / comparison view ── */
    .diff-panel {
        background: #FFFBF0;
        border: 1px solid #FDE68A;
        border-left: 3px solid #F59E0B;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        color: #92400E;
    }

    /* ── Keyword tag ── */
    .kw-tag {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        background: #F0FDFA;
        border: 1px solid #99F6E4;
        border-radius: 20px;
        font-size: 0.75rem;
        color: #0F766E;
        margin: 0.2rem 0.3rem 0.2rem 0;
        transition: all 0.2s ease;
        cursor: default;
    }
    .kw-tag:hover {
        background: #CCFBF1;
        border-color: #5EEAD4;
    }
    .kw-tag.missing {
        background: #FFF1F2;
        border-color: #FECDD3;
        color: #BE123C;
    }

    /* ── Demo button ── */
    .demo-btn-wrapper {
        margin-top: 0.6rem;
    }
    .st-key-demo_load button {
        background: linear-gradient(135deg, #0891B2, #0D9488) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(8, 145, 178, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .st-key-demo_load button:hover {
        box-shadow: 0 4px 16px rgba(8, 145, 178, 0.35) !important;
        transform: translateY(-1px);
    }
</style>
"""

st.markdown(STYLE_CSS, unsafe_allow_html=True)

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

    # Decide active step based on session state
    has_resume = bool(st.session_state.get("resume_text", "").strip())
    has_optimized = bool(st.session_state.get("optimized_resume"))
    has_iq = bool(st.session_state.get("interview_questions"))

    step1_class = "done" if has_optimized else ("active" if has_resume else "")
    step2_class = "done" if has_iq else ("active" if has_optimized else "")
    step3_class = "active" if has_iq else ""

    st.markdown(f"""
        <div style="font-size:0.75rem;margin-bottom:0.5rem;">
            <div style="font-weight:600;color:#99F6E4;margin-bottom:0.6rem;">三步完成优化</div>
            <div class="step-indicator">
                <div class="step-row">
                    <div class="step-circle {step1_class}">{'✓' if has_optimized else '1'}</div>
                    <div class="step-label {step1_class}">输入简历 & 岗位</div>
                </div>
                <div class="step-row">
                    <div class="step-circle {step2_class}">{'✓' if has_iq else '2'}</div>
                    <div class="step-label {step2_class}">AI 优化 & 分析</div>
                </div>
                <div class="step-row">
                    <div class="step-circle {step3_class}">3</div>
                    <div class="step-label {step3_class}">生成面试题库</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Privacy badge
    st.markdown("""
        <div class="privacy-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5EEAD4" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            上传内容仅用于本次分析，不保存或共享
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="font-size:0.72rem;color:#7AADA9;margin-top:1.5rem;line-height:1.5;">
            Powered by Streamlit<br>& 通义千问
        </div>
    """, unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown('<div class="page-title">简历优化中心</div>', unsafe_allow_html=True)

# ====================================================================
#  SHARED INPUT
# ====================================================================
st.markdown('<div class="shared-input-section">', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])

# Sample resume content
SAMPLE_RESUME = """张三 | 高级 Python 工程师 | 5年经验
zhangsan@email.com | 138-0000-0000 | github.com/zhangsan

【个人优势】
- 主导电商平台微服务架构重构，峰值QPS从2k提升至8k
- 带领4人团队完成3条业务线的后端系统设计与落地

【工作经历】
ABC科技 | 高级后端工程师 | 2021.03 - 至今
- 主导订单系统微服务拆分，接口延迟从800ms降至120ms
- 搭建统一网关层，实现限流/熔断/灰度发布，系统可用性99.97%
- 设计数据同步方案，解决跨库事务一致性问题

DEF软件 | Python开发工程师 | 2019.07 - 2021.02
- 负责内部ERP系统核心模块开发（FastAPI + PostgreSQL）
- 参与数据分析平台搭建，日均处理50万条业务数据

【项目经验】
智能客服系统 | 主力后端 | 2022.06 - 2022.12
- 基于RAG架构实现知识库问答，准确率91%
- 优化向量检索性能，查询耗时从3s降至0.3s

【技能】
Python, FastAPI, Django, PostgreSQL, Redis, Kafka, Docker, K8s, AWS

【教育背景】
XX大学 计算机科学与技术 本科 2015 - 2019"""

with col_left:
    resume_text = st.text_area(
        "简历内容",
        height=260,
        placeholder="在此粘贴您的简历内容，或点击下方「加载示例简历」体验...",
        value=st.session_state.get("resume_text", ""),
        key="shared_resume",
        label_visibility="visible",
    )

    c_upload, c_demo = st.columns([2, 1])
    with c_upload:
        fmt_list = get_supported_formats()
        uploaded = st.file_uploader(
            f"上传简历文件（{', '.join(fmt_list)}）",
            type=fmt_list,
            key="shared_upload",
        )
    with c_demo:
        st.markdown('<div class="demo-btn-wrapper">', unsafe_allow_html=True)
        if st.button("加载示例简历", use_container_width=True, key="demo_load"):
            st.session_state.resume_text = SAMPLE_RESUME
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded is not None:
        with st.spinner("解析文件中..."):
            try:
                resume_text = parse_uploaded_file(uploaded)
                st.session_state.resume_text = resume_text
                st.success(f"已解析 {len(resume_text)} 字符")
            except Exception as e:
                st.error(f"解析失败: {e}")

with col_right:
    target_position = st.text_input(
        "目标岗位",
        placeholder="例如：Python 开发工程师",
        value=st.session_state.get("target_position", ""),
        key="shared_position",
    )
    st.session_state.resume_text = resume_text
    st.session_state.target_position = target_position

    # Quick tips for the right column
    if not resume_text.strip():
        st.markdown("""
            <div style="margin-top:0.75rem;padding:0.75rem;background:#F0FDFA;border-radius:8px;border:1px solid #CCFBF1;">
                <div style="font-size:0.75rem;color:#5B8A87;line-height:1.6;">
                    <div style="font-weight:600;color:#0F766E;margin-bottom:0.25rem;">输入格式提示</div>
                    · 包含个人信息、教育背景<br>
                    · 工作/项目经历用 STAR 法则<br>
                    · 技能关键词用逗号分隔<br>
                    · 成果尽量用数字量化
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================
#  TABS
# ====================================================================
t1, t2, t3 = st.tabs(["简历优化", "AI 分析", "面试题生成"])

# Tab descriptions
st.markdown("""
    <div class="tab-desc-row">
        <div class="tab-desc-chip"><span>简历优化</span> — 提升简历可读性与关键词匹配，STAR法则重写</div>
        <div class="tab-desc-chip"><span>AI 分析</span> — 六维度诊断评分，岗位匹配度与改进建议</div>
        <div class="tab-desc-chip"><span>面试题生成</span> — 根据简历与目标岗位，生成个性化面试题</div>
    </div>
""", unsafe_allow_html=True)

# ====================================================================
#  TAB 1 — Resume Optimization
# ====================================================================
with t1:
    c_in, c_out = st.columns([1, 2])

    with c_in:
        st.markdown('<div class="card"><div class="card-title">优化配置</div>', unsafe_allow_html=True)

        opt_style = st.selectbox("优化风格", OPTIMIZATION_STYLES, key="opt_style")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_optimize = st.button("开始优化", use_container_width=True, type="primary", key="btn_opt")
        with cb2:
            btn_clear_opt = st.button("清空结果", use_container_width=True, key="btn_clear_opt")

        if btn_clear_opt:
            st.session_state.optimized_resume = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with c_out:
        st.markdown('<div class="card"><div class="card-title">优化结果</div>', unsafe_allow_html=True)

        if st.session_state.get("optimized_resume"):
            opt_resume = st.session_state.optimized_resume
            # Split AI output into diagnosis and optimized parts for comparison view
            diag_marker = "【简历诊断】"
            opt_marker = "【优化后简历】"

            if diag_marker in opt_resume and opt_marker in opt_resume:
                diag_part = opt_resume.split(opt_marker)[0].replace(diag_marker, "").strip()
                resume_part = opt_resume.split(opt_marker)[1]
                if "【优化对比】" in resume_part:
                    resume_part = resume_part.split("【优化对比】")[0].strip()
                if "【HR视角点评】" in resume_part:
                    resume_part = resume_part.split("【HR视角点评】")[0].strip()
            else:
                diag_part = ""
                resume_part = opt_resume

            col_before, col_after = st.columns(2)
            with col_before:
                st.markdown('<div style="font-size:0.8rem;font-weight:600;color:#A8A29E;margin-bottom:0.4rem;">原稿摘要</div>', unsafe_allow_html=True)
                st.text_area(
                    "原始简历",
                    value=st.session_state.get("resume_text", "")[:400] + ("..." if len(st.session_state.get("resume_text", "")) > 400 else ""),
                    height=240,
                    disabled=True,
                    label_visibility="collapsed",
                    key="before_opt",
                )
            with col_after:
                st.markdown('<div style="font-size:0.8rem;font-weight:600;color:#0D9488;margin-bottom:0.4rem;">优化后 <span style="font-size:0.7rem;background:#F0FDFA;padding:0.15rem 0.4rem;border-radius:4px;">AI 润色</span></div>', unsafe_allow_html=True)
                st.text_area(
                    "优化后简历",
                    value=resume_part if resume_part else opt_resume,
                    height=240,
                    disabled=True,
                    label_visibility="collapsed",
                    key="after_opt",
                )

            # Diff highlights panel
            if diag_part:
                with st.expander("查看诊断摘要与改进要点"):
                    st.markdown(f'<div class="diff-panel">{diag_part.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("复制优化结果", use_container_width=True, key="btn_copy_opt"):
                    st.code(resume_part if resume_part else opt_resume)
                    st.success("内容已显示在上方，可直接选中复制")
            with cc2:
                st.download_button(
                    "下载简历",
                    data=resume_part if resume_part else opt_resume,
                    file_name="optimized_resume.txt",
                    use_container_width=True,
                    key="btn_dl_opt",
                )
        else:
            st.markdown(
                '<div class="empty-state">'
                '<p style="font-size:1.5rem;margin-bottom:0.5rem;">📋</p>'
                '<p>输入简历并配置风格后</p>'
                '<p>点击"开始优化"即可获得 AI 润色结果</p>'
                '<p style="font-size:0.75rem;color:#A8A29E;margin-top:0.75rem;">优化后支持对比查看与一键下载</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if btn_optimize:
        if not resume_text.strip():
            st.warning("请先在顶部输入简历内容")
        elif not target_position.strip():
            st.warning("请先输入目标岗位")
        else:
            with st.spinner("AI 正在优化简历，预计需要 10-15 秒..."):
                try:
                    prompt = build_optimize_prompt(resume_text, target_position, opt_style)
                    result = call_qwen_api_with_retry(prompt)
                    st.session_state.optimized_resume = result
                    st.rerun()
                except Exception as e:
                    st.error(f"优化失败: {e}")

# ====================================================================
#  TAB 2 — AI Analysis
# ====================================================================
with t2:
    c_in, c_out = st.columns([1, 2])

    with c_in:
        st.markdown('<div class="card"><div class="card-title">分析模式</div>', unsafe_allow_html=True)

        btn_quick = st.button("快速扫描 (本地)", use_container_width=True, key="btn_quick")
        st.caption("无需联网，秒级检测简历缺陷")
        st.markdown("<br>", unsafe_allow_html=True)

        btn_analyze = st.button("AI 深度分析", use_container_width=True, type="primary", key="btn_ai_analysis")
        st.caption("大模型六维度诊断，约需 10-20 秒")

        st.markdown("<br>", unsafe_allow_html=True)
        btn_clear_analysis = st.button("清除分析结果", use_container_width=True, key="btn_clear_analysis")
        if btn_clear_analysis:
            st.session_state.ai_analysis_result = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with c_out:
        st.markdown('<div class="card"><div class="card-title">分析报告</div>', unsafe_allow_html=True)

        result = st.session_state.get("ai_analysis_result")
        if result:
            overall = result.get("overall_score", 0)
            match_pct = result.get("match_percentage", 0)
            lang_q = result.get("language_quality", 0)
            kw_match = result.get("keyword_match", 0)

            badge_class = (
                "score-s" if overall >= 90 else
                "score-a" if overall >= 80 else
                "score-b" if overall >= 60 else
                "score-c" if overall >= 40 else "score-d"
            )

            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f'<div class="score-badge {badge_class}">{overall}</div>', unsafe_allow_html=True)
                st.markdown('<div style="text-align:center;margin-top:0.4rem;font-weight:600;color:#0F766E;">综合评分</div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="score-badge {badge_class}">{match_pct}%</div>', unsafe_allow_html=True)
                st.markdown('<div style="text-align:center;margin-top:0.4rem;font-weight:600;color:#0F766E;">岗位匹配度</div>', unsafe_allow_html=True)

            # Keyword extraction panel
            raw = result.get("diagnosis_raw")
            if raw:
                diag = raw.get("diagnosis", {})
                kw_info = diag.get("keyword_match", {})
                matched = kw_info.get("matched", [])
                missing = kw_info.get("missing", [])

                if matched or missing:
                    st.markdown('<div style="margin-top:1rem;font-weight:600;color:#0F766E;font-size:0.9rem;">关键词分析</div>', unsafe_allow_html=True)
                    if matched:
                        st.markdown('<div style="font-size:0.75rem;color:#5B8A87;margin:0.25rem 0;">已匹配</div>', unsafe_allow_html=True)
                        st.markdown(" ".join([f'<span class="kw-tag">{kw}</span>' for kw in matched[:12]]), unsafe_allow_html=True)
                    if missing:
                        st.markdown('<div style="font-size:0.75rem;color:#5B8A87;margin:0.5rem 0 0.25rem;">建议补充</div>', unsafe_allow_html=True)
                        st.markdown(" ".join([f'<span class="kw-tag missing">{kw}</span>' for kw in missing[:12]]), unsafe_allow_html=True)

            # Defect summary badges
            defect_s = result.get("defect_summary")
            if defect_s:
                st.markdown('<div style="margin-top:1rem;text-align:center;">', unsafe_allow_html=True)
                hc, mc, lc = defect_s.get("high", 0), defect_s.get("medium", 0), defect_s.get("low", 0)
                if hc: st.markdown(f'<span class="quick-scan-badge badge-high">严重 {hc}</span>', unsafe_allow_html=True)
                if mc: st.markdown(f'<span class="quick-scan-badge badge-medium">中等 {mc}</span>', unsafe_allow_html=True)
                if lc: st.markdown(f'<span class="quick-scan-badge badge-low">轻微 {lc}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Progress bars
            st.markdown(
                f'<div style="margin-top:1.25rem;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:0.2rem;">'
                f'<span style="color:#78716C;font-size:0.85rem;">语言质量</span>'
                f'<span style="font-weight:600;color:#0F766E;font-size:0.85rem;">{lang_q}</span>'
                f'</div>'
                f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{lang_q}%;background:linear-gradient(90deg,#0D9488,#14B8A6);"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-top:0.75rem;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:0.2rem;">'
                f'<span style="color:#78716C;font-size:0.85rem;">关键词匹配</span>'
                f'<span style="font-weight:600;color:#0F766E;font-size:0.85rem;">{kw_match}</span>'
                f'</div>'
                f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{kw_match}%;background:linear-gradient(90deg,#0D9488,#2DD4BF);"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Industry fit
            raw = result.get("diagnosis_raw")
            if raw and raw.get("industry_fit"):
                st.markdown(
                    f'<div style="margin-top:1rem;padding:0.75rem 1rem;background:#F0FDFA;border:1px solid #99F6E4;border-radius:8px;">'
                    f'<span style="font-weight:600;color:#0F766E;">最适合方向：</span>'
                    f'<span style="color:#134E4A;">{raw["industry_fit"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Suggestions
            suggestions = result.get("suggestions", [])
            if suggestions:
                st.markdown('<h4 style="font-weight:600;color:#0F766E;margin-top:1.25rem;margin-bottom:0.75rem;">优化建议</h4>', unsafe_allow_html=True)
                for sg in suggestions:
                    priority = sg.get("priority", "medium")
                    title = sg.get("title", "")
                    items = sg.get("items", [])
                    if not items:
                        continue
                    badge = "🔴" if priority == "high" else ("🟠" if priority == "medium" else "🟢")
                    with st.expander(f"{badge} {title}"):
                        for item in items:
                            st.write(f"- {item}")
        else:
            st.markdown(
                '<div class="empty-state">'
                '<p style="font-size:1.5rem;margin-bottom:0.5rem;">🔍</p>'
                '<p>输入简历和岗位后</p>'
                '<p>选择"快速扫描"获取即时反馈</p>'
                '<p>或"AI 深度分析"获得完整六维度诊断报告</p>'
                '<p style="font-size:0.75rem;color:#A8A29E;margin-top:0.75rem;">分析结果包含关键词匹配、评分与改进建议</p>'
                '</div>',
                unsafe_allow_html=True,
            )

        # AI disclaimer
        st.markdown(
            '<div style="margin-top:1rem;padding:0.5rem 0.75rem;font-size:0.7rem;color:#A8A29E;text-align:center;border-top:1px solid #CCFBF1;">'
            '智能优化仅供参考，最终内容由您把控。上传内容仅用于本次分析，不会保存或共享。'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # -- Quick scan --
    if btn_quick:
        if not resume_text.strip():
            st.warning("请先在顶部输入简历内容")
        else:
            with st.spinner("正在本地分析..."):
                detector = ResumeDefectDetector()
                defects = detector.detect_all_defects(resume_text)
                severity = detector.get_severity_summary(defects)
                suggestions = detector.generate_optimization_suggestions(resume_text)
                st.session_state.ai_analysis_result = {
                    "overall_score": max(30, 100 - severity["high"] * 15 - severity["medium"] * 8 - severity["low"] * 3),
                    "match_percentage": 0,
                    "language_quality": max(30, 100 - severity["medium"] * 10 - severity["low"] * 5),
                    "keyword_match": 0,
                    "suggestions": suggestions.get("suggestions", []),
                    "defect_summary": severity,
                }
                st.rerun()

    # -- AI Deep Analysis --
    if btn_analyze:
        if not resume_text.strip():
            st.warning("请先在顶部输入简历内容")
        elif not target_position.strip():
            st.warning("请先输入目标岗位")
        else:
            with st.spinner("正在进行 AI 深度分析，预计需要 10-20 秒..."):
                try:
                    prompt = build_resume_diagnosis_prompt(resume_text, target_position)
                    api_result = call_qwen_api_with_retry(prompt)
                    diag_data = json.loads(api_result)
                    d = diag_data.get("diagnosis", {})
                    st.session_state.ai_analysis_result = {
                        "overall_score": diag_data.get("overall_score", 0),
                        "match_percentage": d.get("keyword_match", {}).get("score", 0),
                        "language_quality": d.get("language", {}).get("score", 0),
                        "keyword_match": d.get("keyword_match", {}).get("score", 0),
                        "suggestions": [
                            {"priority": "high", "title": "优先修改", "items": diag_data.get("top_3_fixes", [])},
                            {"priority": "medium", "title": "完整度", "items": d.get("completeness", {}).get("issues", [])},
                            {"priority": "medium", "title": "量化建议", "items": d.get("quantification", {}).get("suggestions", [])},
                            {"priority": "low", "title": "语言优化", "items": d.get("language", {}).get("weak_phrases", [])},
                        ],
                        "diagnosis_raw": diag_data,
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"AI 分析失败: {e}")

# ====================================================================
#  TAB 3 — Interview Questions
# ====================================================================
with t3:
    c_in, c_out = st.columns([1, 2])

    with c_in:
        st.markdown('<div class="card"><div class="card-title">出题配置</div>', unsafe_allow_html=True)

        difficulty = st.selectbox("难度级别", INTERVIEW_DIFFICULTIES, key="iq_diff")
        q_types = st.multiselect("题目类型", INTERVIEW_QUESTION_TYPES, default=["简答题", "项目手撕题"], key="iq_types")
        scope = st.selectbox("出题范围", INTERVIEW_SCOPES, key="iq_scope")
        q_count = st.slider("题目数量", 3, 15, 5, key="iq_count")

        btn_gen = st.button("生成面试题", use_container_width=True, type="primary", key="btn_gen_iq")
        btn_clear_iq = st.button("清除题库", use_container_width=True, key="btn_clear_iq")
        if btn_clear_iq:
            st.session_state.interview_questions = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with c_out:
        st.markdown('<div class="card"><div class="card-title">面试题库</div>', unsafe_allow_html=True)

        iq = st.session_state.get("interview_questions")
        if iq:
            questions = iq.get("questions", [])
            for idx, q in enumerate(questions, 1):
                qt = q.get("type", "")
                qd = q.get("difficulty", "")
                with st.expander(f"第{idx}题  [{qd}] {qt}"):
                    st.markdown(f"**题目：** {q.get('question', '无')}")
                    st.markdown("**答案：**")
                    st.info(q.get("answer", "无"))
                    if q.get("answer_guide"):
                        st.markdown("**答题思路：**")
                        st.write(q.get("answer_guide"))
                    if q.get("answer_script"):
                        st.markdown("**高分回答：**")
                        st.success(q.get("answer_script"))

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    "导出 JSON",
                    data=json.dumps(questions, ensure_ascii=False, indent=2),
                    file_name="interview_questions.json",
                    use_container_width=True,
                    key="btn_dl_json",
                )
            with dl2:
                st.download_button(
                    "导出完整题库",
                    data=json.dumps(iq, ensure_ascii=False, indent=2),
                    file_name="interview_bank.json",
                    use_container_width=True,
                    key="btn_dl_full",
                )
        else:
            st.markdown(
                '<div class="empty-state">'
                '<p style="font-size:1.5rem;margin-bottom:0.5rem;">📋</p>'
                '<p>建议先完成「简历优化」后再生成面试题</p>'
                '<p>配置难度与题型后点击"生成面试题"</p>'
                '<p>每题附带标准答案、答题思路与高分话术</p>'
                '<p style="font-size:0.75rem;color:#A8A29E;margin-top:0.75rem;">基于真实简历内容，千人千题</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if btn_gen:
        if not resume_text.strip():
            st.warning("请先在顶部输入简历内容")
        elif not q_types:
            st.warning("请至少选择一种题目类型")
        else:
            with st.spinner("正在生成个性化面试题..."):
                try:
                    parsed = parse_resume_text(resume_text)
                    summary = resume_to_summary(parsed)
                    tech_stack = parsed.get("skills", {}).get("technical", [])
                    highlights = []
                    for proj in parsed.get("projects", []):
                        if proj.get("highlights"):
                            highlights.extend(proj["highlights"])
                        if proj.get("description"):
                            highlights.append(proj["description"][:50])

                    prompt = build_interview_question_prompt(
                        resume_summary=summary,
                        technical_stack=tech_stack,
                        project_highlights=highlights[:5],
                        difficulty=difficulty,
                        question_types=q_types,
                        scope=scope,
                        question_count=q_count,
                    )
                    result = call_qwen_api_with_retry(prompt)
                    st.session_state.interview_questions = json.loads(result)
                    st.rerun()
                except Exception as e:
                    st.error(f"生成失败: {e}")
