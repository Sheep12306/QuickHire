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
from api_client import call_qwen_api_with_retry, safe_json_parse
from prompt_builder import (
    build_interview_coach_prompt,
    build_answer_scoring_prompt,
    build_weakness_reinforcement_prompt,
    build_interview_summary_prompt,
)
from resume_parser import parse_resume_text, resume_to_summary
from data_service import ResumeService, InterviewService
from components.shared_sidebar import render_shared_sidebar

require_auth()

st.set_page_config(
    page_title="AI面试教练 - 快克简历优化",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────
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
        margin-bottom: 1.5rem;
    }

    .card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #CCFBF1;
        margin-bottom: 1rem;
    }
    .card-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        color: #0F766E;
        margin-bottom: 1rem;
    }

    .question-card {
        background: linear-gradient(135deg, #F0FDFA 0%, #FFFFFF 100%);
        border-radius: 12px;
        padding: 2rem;
        border: 2px solid #5EEAD4;
        margin-bottom: 1.5rem;
    }
    .question-num {
        font-size: 0.8rem;
        color: #5B8A87;
        margin-bottom: 0.5rem;
    }
    .question-text {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0F766E;
        line-height: 1.7;
    }

    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
    }

    .dim-bar {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .dim-label {
        width: 60px;
        font-size: 0.78rem;
        color: #5B8A87;
        text-align: right;
    }
    .dim-fill {
        height: 10px;
        border-radius: 5px;
        background: linear-gradient(90deg, #0D9488, #2DD4BF);
        transition: width 0.5s ease;
    }
    .dim-score {
        width: 35px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #0F766E;
    }

    .session-progress {
        text-align: center;
        font-size: 0.85rem;
        color: #5B8A87;
        margin-bottom: 1rem;
    }
</style>
"""
st.markdown(STYLE_CSS, unsafe_allow_html=True)

if not is_api_configured():
    st.warning("⚠️ 通义千问 API 未配置，AI 功能不可用。请前往「个人中心 → API配置」设置你的 DashScope API Key。")
    st.page_link("pages/05_profile.py", label="⚙️ 前往配置 API")

render_shared_sidebar(current_page="coach")

st.markdown('<div class="page-title">🎤 AI 面试教练</div>', unsafe_allow_html=True)

# ── Initialize session keys ───────────────────────────────────
for key, default in [
    ("coach_questions", None),
    ("coach_current_q", 0),
    ("coach_session_scores", []),
    ("coach_session_qa", []),
    ("coach_started", False),
    ("coach_feedback", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

INTERVIEW_TYPES = ["技术面", "HR面", "综合面"]
DIFFICULTIES = ["入门", "基础", "中等", "面试高频", "深度深挖"]

tab1, tab2, tab3 = st.tabs(["🎯 模拟面试", "💪 针对性强化", "📋 答题记录"])

# ====================================================================
#  TAB 1 — Mock Interview
# ====================================================================
with tab1:
    col_setup, col_interview = st.columns([1, 2])

    with col_setup:
        st.markdown('<div class="card"><div class="card-title">面试设置</div>', unsafe_allow_html=True)

        interview_type = st.selectbox("面试类型", INTERVIEW_TYPES, key="coach_type")
        difficulty = st.selectbox("难度级别", DIFFICULTIES, key="coach_diff")
        q_count = st.slider("题目数量", 3, 10, 5, key="coach_count")

        if st.button("🎯 开始模拟面试", type="primary", use_container_width=True):
            user_id = st.session_state.user_id
            latest = ResumeService.get_latest_resume(user_id)

            if not latest or not latest.get("original_content"):
                st.error("请先在「简历优化中心」上传简历")
            else:
                # Find weak areas from history
                weak_areas = []
                answers = InterviewService.get_answers(user_id)
                for a in answers:
                    if a.get("ai_feedback"):
                        try:
                            fb = json.loads(a["ai_feedback"])
                            if fb.get("weaknesses"):
                                weak_areas.extend(fb["weaknesses"])
                        except (json.JSONDecodeError, TypeError):
                            pass
                weak_areas = list(set(weak_areas))[:5]

                parsed = parse_resume_text(latest["original_content"])
                summary = resume_to_summary(parsed)
                tech_stack = parsed.get("skills", {}).get("technical", [])

                with st.spinner("AI正在为你量身出题..."):
                    try:
                        prompt = build_interview_coach_prompt(
                            resume_summary=summary,
                            technical_stack=tech_stack,
                            weak_areas=weak_areas,
                            interview_type=interview_type,
                            difficulty=difficulty,
                            question_count=q_count,
                        )
                        result = call_qwen_api_with_retry(prompt)
                        data = safe_json_parse(result)
                        st.session_state.coach_questions = data.get("questions", [])
                        st.session_state.coach_current_q = 0
                        st.session_state.coach_session_scores = []
                        st.session_state.coach_session_qa = []
                        st.session_state.coach_started = True
                        st.session_state.coach_feedback = {}
                        st.rerun()
                    except Exception as e:
                        st.error(f"出题失败: {e}")

        if st.button("🛑 结束面试", use_container_width=True):
            st.session_state.coach_started = False
            st.session_state.coach_questions = None
            st.session_state.coach_current_q = 0
            st.session_state.coach_session_scores = []
            st.session_state.coach_session_qa = []
            st.session_state.coach_feedback = {}
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_interview:
        questions = st.session_state.coach_questions or []
        current_q = st.session_state.coach_current_q

        if not st.session_state.coach_started or not questions:
            st.markdown(
                '<div class="card" style="text-align:center;padding:3rem;">'
                '<p style="font-size:3rem;margin-bottom:1rem;">🎤</p>'
                '<p style="font-size:1.1rem;color:#5B8A87;">配置面试参数后点击"开始模拟面试"</p>'
                '<p style="font-size:0.8rem;color:#A8A29E;">AI 将根据你的简历内容量身出题</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        elif current_q >= len(questions):
            # All questions answered — show summary
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("## 🎉 模拟面试完成！")

            scores = st.session_state.coach_session_scores
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0

            grade_color = (
                "#0D9488" if avg_score >= 90 else "#14B8A6" if avg_score >= 80
                else "#F59E0B" if avg_score >= 60 else "#EF4444"
            )
            st.markdown(
                f'<div class="score-badge" style="background:{grade_color};width:100px;height:100px;font-size:2rem;margin:1rem auto;">'
                f'{avg_score}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="text-align:center;font-weight:600;color:#0F766E;margin-bottom:1.5rem;">'
                f'综合评分</div>',
                unsafe_allow_html=True,
            )

            # Save answers to DB
            user_id = st.session_state.user_id
            session_qa = st.session_state.coach_session_qa
            if session_qa:
                with st.spinner("正在生成面试总结..."):
                    try:
                        summary_prompt = build_interview_summary_prompt(session_qa)
                        summary_result = call_qwen_api_with_retry(summary_prompt)
                        summary_data = safe_json_parse(summary_result)

                        st.markdown("### 📊 AI 总结报告")
                        st.write(summary_data.get("overall_assessment", {}).get("summary", ""))

                        strengths = summary_data.get("top_3_strengths", [])
                        improvements = summary_data.get("top_3_improvements", [])

                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**✅ 你的强项**")
                            for s in strengths:
                                st.markdown(f"- {s}")
                        with c2:
                            st.markdown("**🔧 需要改进**")
                            for imp in improvements:
                                st.markdown(f"- {imp}")

                        study_plan = summary_data.get("study_plan", [])
                        if study_plan:
                            st.markdown("### 📝 学习计划")
                            for sp in study_plan:
                                st.markdown(f"- {sp}")

                        next_tip = summary_data.get("next_interview_tip", "")
                        if next_tip:
                            st.info(f"💡 {next_tip}")
                    except Exception as e:
                        st.error(f"生成总结失败: {e}")

                for item in session_qa:
                    try:
                        InterviewService.save_answer(
                            user_id=user_id,
                            question_text=item.get("question", ""),
                            user_answer=item.get("answer", ""),
                            ai_score=item.get("score"),
                            ai_feedback=json.dumps(item.get("full_feedback", {}), ensure_ascii=False),
                        )
                    except Exception:
                        pass

            if st.button("🔄 重新开始", type="primary"):
                st.session_state.coach_started = False
                st.session_state.coach_questions = None
                st.session_state.coach_current_q = 0
                st.session_state.coach_session_scores = []
                st.session_state.coach_session_qa = []
                st.session_state.coach_feedback = {}
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show current question
            q = questions[current_q]
            st.markdown('<div class="session-progress">'
                        f'第 {current_q + 1}/{len(questions)} 题</div>',
                        unsafe_allow_html=True)

            st.markdown(
                f'<div class="question-card">'
                f'<div class="question-num">Question {current_q + 1} · {q.get("type", "")} · {q.get("difficulty", "")}</div>'
                f'<div class="question-text">{q.get("question", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            user_answer = st.text_area(
                "你的回答",
                placeholder="在此输入你的回答...",
                height=150,
                key=f"answer_{current_q}",
            )

            # Show feedback if already scored
            feedback = st.session_state.coach_feedback.get(current_q)
            if feedback:
                st.markdown("### 📊 评分结果")
                overall = feedback.get("overall_score", 0)
                fb_color = (
                    "#0D9488" if overall >= 90 else "#14B8A6" if overall >= 80
                    else "#F59E0B" if overall >= 60 else "#EF4444"
                )
                st.markdown(
                    f'<div class="score-badge" style="background:{fb_color};">{overall}</div>',
                    unsafe_allow_html=True,
                )

                dims = feedback.get("dimensions", {})
                for dim_name, dim_data in dims.items():
                    score = dim_data.get("score", 0)
                    comment = dim_data.get("comment", "")
                    st.markdown(
                        f'<div class="dim-bar">'
                        f'<div class="dim-label">{dim_name}</div>'
                        f'<div style="flex:1;background:#E7E5E4;border-radius:5px;height:10px;">'
                        f'<div class="dim-fill" style="width:{score}%;"></div>'
                        f'</div>'
                        f'<div class="dim-score">{score}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption(comment)

                improved = feedback.get("improved_answer", "")
                if improved:
                    with st.expander("🏆 高分回答示例", expanded=False):
                        st.markdown(improved)

                missing = feedback.get("key_missing_points", [])
                if missing:
                    st.markdown("**⚠️ 遗漏的关键点**")
                    for m in missing:
                        st.markdown(f"- {m}")

                encouragement = feedback.get("encouragement", "")
                if encouragement:
                    st.success(encouragement)

            if st.button("提交答案", type="primary", use_container_width=True, key=f"submit_{current_q}"):
                if not user_answer.strip():
                    st.warning("请输入你的回答")
                else:
                    expected = "\n".join(q.get("expected_answer_points", []))
                    with st.spinner("AI 正在评分..."):
                        try:
                            score_prompt = build_answer_scoring_prompt(
                                question_text=q.get("question", ""),
                                expected_answer_points=expected,
                                user_answer=user_answer,
                                question_type=q.get("type", ""),
                            )
                            score_result = call_qwen_api_with_retry(score_prompt)
                            fb = safe_json_parse(score_result)

                            st.session_state.coach_feedback[current_q] = fb
                            st.session_state.coach_session_scores.append(fb.get("overall_score", 0))
                            st.session_state.coach_session_qa.append({
                                "number": current_q + 1,
                                "question": q.get("question", ""),
                                "answer": user_answer,
                                "score": fb.get("overall_score", 0),
                                "full_feedback": fb,
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"评分失败: {e}")

            if feedback:
                if st.button("下一题 ➡️", use_container_width=True, key=f"next_{current_q}"):
                    st.session_state.coach_current_q = current_q + 1
                    st.rerun()

# ====================================================================
#  TAB 2 — Targeted Practice
# ====================================================================
with tab2:
    user_id = st.session_state.user_id

    st.markdown('<div class="card"><div class="card-title">📈 薄弱环节分析</div>', unsafe_allow_html=True)

    answers = InterviewService.get_answers(user_id)

    if not answers:
        st.info("还没有答题记录，请先在「模拟面试」中完成至少一次答题")
    else:
        # Analyze weak dimensions
        dim_scores = {
            "accuracy": [], "depth": [], "structure": [], "expression": [], "highlights": []
        }
        weak_areas = []

        for a in answers:
            if a.get("ai_feedback"):
                try:
                    fb = json.loads(a["ai_feedback"])
                    dims = fb.get("dimensions", {})
                    for d_name, d_data in dims.items():
                        if d_name in dim_scores:
                            dim_scores[d_name].append(d_data.get("score", 0))
                    if fb.get("weaknesses"):
                        weak_areas.extend(fb["weaknesses"])
                except (json.JSONDecodeError, TypeError):
                    pass

        # Show dimension averages
        avg_dims = {}
        for d_name, scores in dim_scores.items():
            avg_dims[d_name] = round(sum(scores) / len(scores), 1) if scores else 0

        st.markdown("**各维度平均得分**")
        cols = st.columns(5)
        dim_labels = {"accuracy": "准确性", "depth": "深度", "structure": "结构", "expression": "表达", "highlights": "亮点"}
        for i, (d_name, label) in enumerate(dim_labels.items()):
            score = avg_dims.get(d_name, 0)
            color = "#0D9488" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
            cols[i].markdown(
                f'<div style="text-align:center;background:#FFF;border-radius:8px;padding:0.75rem;border:1px solid #CCFBF1;">'
                f'<div style="font-size:1.3rem;font-weight:700;color:{color};">{score}</div>'
                f'<div style="font-size:0.72rem;color:#5B8A87;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        low_dims = [k for k, v in avg_dims.items() if v < 60]
        weak_areas = list(set(weak_areas))[:5]

        if low_dims or weak_areas:
            st.markdown("### 🎯 针对性强化训练")

            latest = ResumeService.get_latest_resume(user_id)
            summary = ""
            if latest:
                parsed = parse_resume_text(latest.get("original_content", ""))
                summary = resume_to_summary(parsed)

            if st.button("生成强化训练题", type="primary"):
                with st.spinner("AI 正在生成针对性题目..."):
                    try:
                        prompt = build_weakness_reinforcement_prompt(
                            weak_areas=weak_areas,
                            low_score_dimensions=low_dims,
                            resume_summary=summary,
                            question_count=3,
                        )
                        result = call_qwen_api_with_retry(prompt)
                        data = safe_json_parse(result)
                        st.session_state.reinforcement_data = data
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {e}")
        else:
            st.success("🎉 所有维度表现良好，暂无薄弱项！")

    st.markdown('</div>', unsafe_allow_html=True)

    # Show reinforcement questions
    rein_data = st.session_state.get("reinforcement_data")
    if rein_data:
        st.markdown('<div class="card"><div class="card-title">强化训练题</div>', unsafe_allow_html=True)
        st.markdown(f"**训练目标**: {rein_data.get('training_focus', '')}")

        for i, q in enumerate(rein_data.get("questions", []), 1):
            with st.expander(f"题{i}: {q.get('question', '')[:60]}...", expanded=i == 1):
                st.markdown(f"**题目**: {q.get('question', '')}")
                st.markdown(f"**针对薄弱点**: {q.get('target_weakness', '')}")
                st.markdown(f"**答题指引**: {q.get('answer_guide', '')}")
                concepts = q.get("key_concepts", [])
                if concepts:
                    st.markdown("**关键概念**: " + ", ".join(concepts))

        tips = rein_data.get("study_tips", [])
        if tips:
            st.markdown("### 📚 学习建议")
            for tip in tips:
                st.markdown(f"- {tip}")

        st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================
#  TAB 3 — Answer History
# ====================================================================
with tab3:
    user_id = st.session_state.user_id
    answers = InterviewService.get_answers(user_id)

    if not answers:
        st.info("还没有答题记录")
    else:
        total = len(answers)
        avg = round(sum(a.get("ai_score", 0) or 0 for a in answers) / total, 1) if total > 0 else 0
        best = max((a.get("ai_score") or 0) for a in answers) if answers else 0
        recent_5 = [a for a in answers[:5] if a.get("ai_score")]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("总答题数", total)
        c2.metric("平均分", avg)
        c3.metric("最高分", best)
        recent_avg = round(sum(a["ai_score"] for a in recent_5) / len(recent_5), 1) if recent_5 else 0
        c4.metric("最近5题均分", recent_avg)

        st.markdown("---")

        for a in answers:
            score = a.get("ai_score")
            score_color = "#0D9488" if score and score >= 80 else "#F59E0B" if score and score >= 60 else "#EF4444"
            date = (a.get("created_at") or "")[:10]

            with st.expander(
                f"[{date}] {a.get('question_text', '')[:80]}...  — {score or 'N/A'}分",
                expanded=False,
            ):
                st.markdown(f"**题目**: {a.get('question_text', '')}")
                st.markdown(f"**你的回答**: {a.get('user_answer', '')}")
                if score:
                    st.markdown(f"**AI评分**: :{'green' if score >= 80 else 'orange' if score >= 60 else 'red'}[{score}分]")

                if a.get("ai_feedback"):
                    try:
                        fb = json.loads(a["ai_feedback"])
                        dims = fb.get("dimensions", {})
                        if dims:
                            cols = st.columns(len(dims))
                            for i, (d_name, d_data) in enumerate(dims.items()):
                                s = d_data.get("score", 0)
                                cols[i].metric(d_name, s)

                        improved = fb.get("improved_answer", "")
                        if improved:
                            with st.expander("高分回答示例"):
                                st.markdown(improved)
                    except (json.JSONDecodeError, TypeError):
                        pass
