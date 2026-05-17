import streamlit as st
import json
import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from app import require_auth
from api_config import is_api_configured
from api_client import call_qwen_api_with_retry
from prompt_builder import build_monthly_report_prompt
from analytics_engine import AnalyticsEngine
from data_service import (
    ResumeService,
    InterviewService,
    ApplicationService,
)
from components.shared_sidebar import render_shared_sidebar
from components.charts import (
    build_radar_chart,
    build_line_chart,
    build_bar_chart,
    build_funnel_chart,
    build_score_distribution,
)

require_auth()

st.set_page_config(
    page_title="数据看板 - 快克简历优化",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    button[data-testid="baseButton-header"],
    button[data-testid="baseButton-header"] *,
    .material-icons {
        font-family: 'Material Icons' !important;
    }

    [data-testid="stSidebarNav"] { display: none !important; }

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

    .main [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F0FDFA 0%, #ECFDF5 100%);
    }

    .page-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F766E;
        margin-bottom: 0.25rem;
    }
    .page-subtitle {
        font-size: 0.9rem;
        color: #5B8A87;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid #CCFBF1;
        text-align: center;
    }
    .metric-value {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F766E;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #5B8A87;
        margin-top: 0.2rem;
    }

    .section-header {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #0F766E;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #CCFBF1;
    }
</style>
"""
st.markdown(STYLE_CSS, unsafe_allow_html=True)

if not is_api_configured():
    st.warning("⚠️ 通义千问 API 未配置，AI 报告功能不可用。请前往「个人中心 → API配置」设置。")
    st.page_link("pages/05_profile.py", label="⚙️ 前往配置 API")

render_shared_sidebar(current_page="analytics")

st.markdown('<div class="page-title">📊 数据看板</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">追踪简历优化进度、面试能力成长与求职进展</div>', unsafe_allow_html=True)

user_id = st.session_state.user_id

# ── Section 1: Key Metrics ─────────────────────────────────────
engine = AnalyticsEngine()
resume_history = engine.resume_improvement_timeline(user_id)
interview_scores = engine.interview_score_history(user_id)
app_stats = engine.application_funnel(user_id)

c1, c2, c3, c4 = st.columns(4)
with c1:
    resume_count = len(resume_history)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{resume_count}</div>'
        f'<div class="metric-label">简历优化次数</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    answer_count = len(interview_scores)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{answer_count}</div>'
        f'<div class="metric-label">面试答题数</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    avg_score = round(sum(s["score"] for s in interview_scores) / len(interview_scores), 1) if interview_scores else 0
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{avg_score}</div>'
        f'<div class="metric-label">面试均分</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    interview_rate = app_stats.get("interview_rate", 0)
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{interview_rate}%</div>'
        f'<div class="metric-label">面试转化率</div></div>',
        unsafe_allow_html=True,
    )

# ── Section 2: Resume Progress ─────────────────────────────────
st.markdown('<div class="section-header">📝 简历优化历程</div>', unsafe_allow_html=True)

radar_data = engine.skill_radar_data(user_id)
if radar_data:
    c1, c2 = st.columns([1, 1])
    with c1:
        if resume_history:
            line_data = [d for d in resume_history if d.get("score") is not None]
            if line_data:
                fig = build_line_chart(
                    line_data, "date", ["score"],
                    title="综合评分趋势",
                    labels={"score": "综合评分"},
                )
                st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = build_radar_chart(radar_data, title="六维度能力雷达图")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("请先在「简历优化中心」完成一次 AI 深度分析，以查看雷达图")

# ── Section 3: Interview Growth ────────────────────────────────
st.markdown('<div class="section-header">🎤 面试能力成长</div>', unsafe_allow_html=True)

if interview_scores:
    c1, c2 = st.columns(2)
    with c1:
        fig = build_line_chart(
            interview_scores[:20], "date", ["score"],
            title="面试分数趋势",
            labels={"score": "得分"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        scores_only = [s["score"] for s in interview_scores]
        fig = build_score_distribution(scores_only, title="得分分布")
        st.plotly_chart(fig, use_container_width=True)

    dim_trends = engine.interview_dimension_trends(user_id)
    if dim_trends:
        dim_labels = {
            "accuracy": "准确性", "depth": "深度",
            "structure": "结构", "expression": "表达", "highlights": "亮点",
        }
        with st.expander("📈 各维度趋势详情"):
            for d_name, points in dim_trends.items():
                if points:
                    label = dim_labels.get(d_name, d_name)
                    fig = build_line_chart(
                        points, "date", ["score"],
                        title=f"{label}趋势",
                        labels={"score": label},
                    )
                    st.plotly_chart(fig, use_container_width=True)

    qtype = engine.question_type_performance(user_id)
    if qtype:
        fig = build_bar_chart(list(qtype.keys()), list(qtype.values()), title="按题型均分")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("请在「AI面试教练」中完成至少一次答题")

# ── Section 4: Weakness Tracking ───────────────────────────────
st.markdown('<div class="section-header">🔍 弱项追踪</div>', unsafe_allow_html=True)

weak_improvements = engine.weak_area_improvement(user_id)
if weak_improvements:
    for w in weak_improvements:
        change = w["improvement"]
        arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        color = "#0D9488" if change > 0 else "#EF4444" if change < 0 else "#5B8A87"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem;'
            f'background:#FFF;border-radius:8px;padding:0.75rem;border:1px solid #CCFBF1;">'
            f'<span style="font-weight:600;color:#0F766E;min-width:80px;">{w["dimension"]}</span>'
            f'<span>{w["first_score"]} → <b style="color:{color};">{w["latest_score"]}</b></span>'
            f'<span>{arrow} {change:+.1f}</span>'
            f'<span style="font-size:0.75rem;color:#A8A29E;">经过{w["sessions"]}次练习</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("完成至少2次答题后可查看弱项进步追踪")

# ── Section 5: Job Search Progress ─────────────────────────────
st.markdown('<div class="section-header">💼 求职进度</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    status_counts = app_stats.get("status_counts", {})
    if status_counts:
        stages = ["applied", "screening", "interview", "offer", "accepted", "rejected"]
        stage_cn = {"applied": "已投递", "screening": "筛选中", "interview": "面试中",
                      "offer": "已Offer", "accepted": "已接受", "rejected": "已拒绝"}
        labels = [stage_cn.get(s, s) for s in stages if status_counts.get(s)]
        values = [status_counts.get(s, 0) for s in stages if status_counts.get(s)]
        if labels:
            fig = build_funnel_chart(labels, values)
            st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("**快速添加投递记录**")
    with st.form("add_application"):
        company = st.text_input("公司名称", placeholder="例如：阿里巴巴")
        position = st.text_input("岗位", placeholder="例如：高级Python开发")
        status = st.selectbox("状态", ["applied", "screening", "interview", "offer", "accepted", "rejected"],
                              format_func=lambda x: {"applied": "已投递", "screening": "筛选中", "interview": "面试中",
                                                     "offer": "已Offer", "accepted": "已接受", "rejected": "已拒绝"}.get(x, x))
        submitted = st.form_submit_button("添加", type="primary", use_container_width=True)
        if submitted and company.strip() and position.strip():
            ApplicationService.add_application(user_id, company.strip(), position.strip(), status)
            st.success("已添加")
            st.rerun()

# Recent applications
apps = ApplicationService.get_applications(user_id)
if apps:
    st.markdown("**最近投递**")
    for a in apps[:5]:
        status_cn = {"applied": "📤 已投递", "screening": "🔍 筛选中", "interview": "🎤 面试中",
                      "offer": "🎉 已Offer", "accepted": "✅ 已接受", "rejected": "❌ 已拒绝"}
        st.markdown(
            f'<span>{a.get("company_name")} · {a.get("position")} · '
            f'{status_cn.get(a.get("status"), a.get("status"))} · '
            f'{(a.get("applied_at") or "")[:10]}</span>',
            unsafe_allow_html=True,
        )

# ── Section 6: AI Monthly Report ──────────────────────────────
st.markdown('<div class="section-header">🤖 AI 综合报告</div>', unsafe_allow_html=True)

if st.button("生成本月综合报告", type="primary"):
    if not resume_history and not interview_scores:
        st.warning("请先积累一些数据再进行综合报告生成")
    else:
        with st.spinner("AI 正在为你撰写本月报告..."):
            try:
                prompt = build_monthly_report_prompt(
                    user_name=st.session_state.get("display_name", "用户"),
                    resume_progress=json.dumps(resume_history, ensure_ascii=False),
                    interview_stats=json.dumps({
                        "total_answers": len(interview_scores),
                        "avg_score": avg_score,
                        "trend": [s["score"] for s in interview_scores[:5]],
                    }, ensure_ascii=False),
                    weak_area_progress=json.dumps(weak_improvements, ensure_ascii=False),
                    application_funnel=json.dumps(app_stats, ensure_ascii=False),
                )
                report = call_qwen_api_with_retry(prompt)
                st.markdown(
                    f'<div style="background:#FFF;border-radius:12px;padding:2rem;border:2px solid #5EEAD4;'
                    f'line-height:1.8;color:#1C1917;">{report}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"报告生成失败: {e}")
