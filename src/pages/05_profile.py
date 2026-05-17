import streamlit as st
import json
import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from app import require_auth
from auth_service import AuthService, AuthError
from data_service import (
    ResumeService,
    InterviewService,
    ApplicationService,
    UserSettingsService,
)
from file_parser import parse_uploaded_file, get_supported_formats
from resume_parser import parse_resume_text, resume_to_summary
from api_config import load_api_config, save_api_config, test_api_connection, is_api_configured
from components.shared_sidebar import render_shared_sidebar

require_auth()

st.set_page_config(
    page_title="个人中心 - 快克简历优化",
    page_icon="⚙️",
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
    .info-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-label {
        width: 80px;
        font-size: 0.85rem;
        color: #5B8A87;
    }
    .info-value {
        font-size: 0.85rem;
        color: #1C1917;
        font-weight: 500;
    }
</style>
"""
st.markdown(STYLE_CSS, unsafe_allow_html=True)

render_shared_sidebar(current_page="profile")

st.markdown('<div class="page-title">⚙️ 个人中心</div>', unsafe_allow_html=True)

user_id = st.session_state.user_id
prefs = UserSettingsService.get_preferences(user_id)

tab0, tab_resume, tab1, tab2, tab3, tab4 = st.tabs(
    ["🔑 API配置", "📄 我的简历", "👤 个人信息", "🔒 修改密码", "⚙️ 偏好设置", "📦 数据管理"]
)

# ── Tab 0: API Config ─────────────────────────────────────────
with tab0:
    st.markdown('<div class="card"><div class="card-title">通义千问 API 配置</div>', unsafe_allow_html=True)

    current_config = load_api_config()
    api_configured = is_api_configured()

    if api_configured:
        st.success("✅ API 已配置")
    else:
        st.warning("⚠️ API 未配置或 Key 无效，请填入你的 DashScope API Key")
        st.markdown("""
        <div style="font-size:0.82rem;color:#5B8A87;margin-bottom:1rem;">
            获取方式：访问 <a href="https://dashscope.console.aliyun.com/apiKey" target="_blank">阿里云 DashScope 控制台</a> 创建 API Key
        </div>
        """, unsafe_allow_html=True)

    new_api_key = st.text_input(
        "DASHSCOPE_API_KEY",
        value=current_config["api_key"] if current_config["api_key"] not in ("your-api-key-here", "your_api_key_here") else "",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx",
    )
    new_base_url = st.text_input("API Base URL", value=current_config["base_url"])
    available_models = [
        "deepseek-chat", "deepseek-reasoner", "deepseek-v4-fast",
        "qwen-plus", "qwen-turbo", "qwen-max",
    ]
    try:
        model_idx = available_models.index(current_config["model"])
    except ValueError:
        model_idx = 0
    new_model = st.selectbox("默认模型", available_models, index=model_idx)

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 保存配置", type="primary", use_container_width=True):
            if new_api_key.strip():
                save_api_config(
                    api_key=new_api_key.strip(),
                    base_url=new_base_url.strip(),
                    model=new_model,
                )
                st.success("API 配置已保存！")
                st.rerun()
            else:
                st.error("API Key 不能为空")

    with col_test:
        if st.button("🔍 测试连接", use_container_width=True):
            with st.spinner("正在测试 API 连接..."):
                result = test_api_connection(api_key=new_api_key.strip() or None)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])

    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab: My Resumes ────────────────────────────────────────────
with tab_resume:
    st.markdown('<div class="card"><div class="card-title">📄 我的简历</div>', unsafe_allow_html=True)

    # Upload new resume directly
    st.markdown("**上传新简历**")
    fmt_list = get_supported_formats()
    uploaded = st.file_uploader(
        f"支持格式：{', '.join(fmt_list)}",
        type=fmt_list,
        key="profile_resume_upload",
        label_visibility="collapsed",
    )
    if uploaded is not None:
        file_content = parse_uploaded_file(uploaded)
        if file_content:
            ResumeService.save_resume(
                user_id=user_id,
                original_content=file_content,
                target_position="",
            )
            st.success("简历已上传并保存")
            st.rerun()

    st.markdown("---")

    # List existing resumes
    history = ResumeService.get_resume_history(user_id)
    if history:
        st.markdown(f"**共 {len(history)} 份简历**")
        for h in history:
            pos = h.get("target_position", "") or "未指定岗位"
            date = (h.get("created_at") or "")[:10]
            is_current = h.get("is_current", False)
            tag = " ✅ 当前" if is_current else ""

            with st.expander(f"v{h['version_number']} · {pos} · {date}{tag}"):
                st.text_area(
                    "原始内容",
                    value=h.get("original_content", ""),
                    height=150,
                    disabled=True,
                    key=f"profile_orig_{h['id']}",
                    label_visibility="collapsed",
                )
                if h.get("optimized_content"):
                    st.text_area(
                        "优化后内容",
                        value=h["optimized_content"],
                        height=150,
                        disabled=True,
                        key=f"profile_opt_{h['id']}",
                        label_visibility="collapsed",
                    )

                c1, c2 = st.columns(2)
                with c1:
                    if not is_current:
                        if st.button("⭐ 设为当前简历", key=f"set_cur_{h['id']}", use_container_width=True):
                            ResumeService.set_current_version(user_id, h["id"])
                            st.rerun()
                with c2:
                    if st.button("✏️ 在优化中心打开", key=f"open_opt_{h['id']}", use_container_width=True):
                        st.session_state.resume_text = h.get("original_content", "")
                        if h.get("optimized_content"):
                            st.session_state.optimized_resume = h["optimized_content"]
                        if h.get("target_position"):
                            st.session_state.target_position = h["target_position"]
                        st.switch_page("pages/02_resume_optimizer.py")
    else:
        st.info("还没有简历记录。上传简历或前往「简历优化中心」创建。")
        st.page_link("pages/02_resume_optimizer.py", label="📝 前往简历优化中心")

    # ── Favorited questions ──
    st.markdown("---")
    st.markdown("**⭐ 收藏的面试题**")
    prefs = UserSettingsService.get_preferences(user_id)
    fav_keys = prefs.get("favorite_questions", [])
    if fav_keys:
        banks = InterviewService.get_question_banks(user_id)
        found = 0
        for bank in banks:
            try:
                questions = json.loads(bank.get("questions_json", "{}")).get("questions", [])
            except (json.JSONDecodeError, TypeError):
                continue
            for q in questions:
                q_text = q.get("question", "")
                q_key = q_text[:80]
                if q_key in fav_keys:
                    found += 1
                    with st.expander(f"⭐ {q_text[:80]}...", expanded=False):
                        st.markdown(f"**题目**: {q_text}")
                        st.markdown(f"**类型**: {q.get('type', '')} · {q.get('difficulty', '')}")
                        if q.get("answer_guide"):
                            st.info(q["answer_guide"])
                        with st.expander("查看答案", expanded=False):
                            st.markdown(q.get("answer", ""))
                    # Remove from fav_keys to track what's found
                    fav_keys.remove(q_key)
        if found == 0:
            st.info("暂无收藏的面试题。在「简历优化中心」生成面试题后可点击 ⭐ 收藏。")
        elif fav_keys:
            st.caption(f"（{len(fav_keys)} 条旧收藏已失效，可能来自已清除的题库）")
    else:
        st.info("暂无收藏的面试题。在「简历优化中心」生成面试题后可点击 ⭐ 收藏。")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 1: Profile ─────────────────────────────────────────────
with tab1:
    st.markdown('<div class="card"><div class="card-title">基本信息</div>', unsafe_allow_html=True)

    email = st.session_state.get("user_email") or ""
    phone = st.session_state.get("user_phone") or ""
    display_name = st.session_state.get("display_name") or ""

    new_name = st.text_input("昵称", value=display_name)
    new_email = st.text_input("邮箱", value=email)
    new_phone = st.text_input("手机号", value=phone)

    if st.button("保存修改", type="primary"):
        try:
            UserSettingsService.update_profile(
                user_id=user_id,
                display_name=new_name.strip(),
                email=new_email.strip() or None,
                phone=new_phone.strip() or None,
            )
            st.session_state.display_name = new_name.strip()
            st.session_state.user_email = new_email.strip() or None
            st.session_state.user_phone = new_phone.strip() or None
            st.success("信息已更新")
        except Exception as e:
            st.error(f"更新失败: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 2: Change Password ─────────────────────────────────────
with tab2:
    st.markdown('<div class="card"><div class="card-title">修改密码</div>', unsafe_allow_html=True)

    old_pw = st.text_input("原密码", type="password", key="old_pw")
    new_pw = st.text_input("新密码", type="password", key="new_pw")
    confirm_pw = st.text_input("确认新密码", type="password", key="confirm_pw")

    if st.button("修改密码", type="primary"):
        if not old_pw or not new_pw or not confirm_pw:
            st.warning("请填写所有密码字段")
        elif new_pw != confirm_pw:
            st.warning("两次输入的新密码不一致")
        elif len(new_pw) < 6:
            st.warning("密码长度不能少于6位")
        else:
            try:
                UserSettingsService.change_password(user_id, old_pw, new_pw)
                st.success("密码修改成功")
            except ValueError as e:
                st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 3: Preferences ─────────────────────────────────────────
with tab3:
    st.markdown('<div class="card"><div class="card-title">偏好设置</div>', unsafe_allow_html=True)

    default_style = st.selectbox(
        "默认优化风格",
        ["简洁专业", "突出业绩", "技术导向", "创新风格"],
        index=["简洁专业", "突出业绩", "技术导向", "创新风格"].index(
            prefs.get("default_style", "简洁专业")
        ) if prefs.get("default_style") in ["简洁专业", "突出业绩", "技术导向", "创新风格"] else 0,
    )
    default_difficulty = st.selectbox(
        "默认面试难度",
        ["入门", "基础", "中等", "面试高频", "深度深挖"],
        index=["入门", "基础", "中等", "面试高频", "深度深挖"].index(
            prefs.get("default_difficulty", "中等")
        ) if prefs.get("default_difficulty") in ["入门", "基础", "中等", "面试高频", "深度深挖"] else 2,
    )
    default_q_count = st.slider(
        "默认面试题数", 3, 15,
        prefs.get("default_q_count", 5),
    )

    if st.button("保存偏好", type="primary"):
        UserSettingsService.save_preferences(user_id, {
            "default_style": default_style,
            "default_difficulty": default_difficulty,
            "default_q_count": default_q_count,
        })
        st.success("偏好已保存")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 4: Data Management ─────────────────────────────────────
with tab4:
    st.markdown('<div class="card"><div class="card-title">数据导出</div>', unsafe_allow_html=True)

    if st.button("📥 导出我的所有数据为 JSON"):
        resumes = ResumeService.get_resume_history(user_id)
        answers = InterviewService.get_answers(user_id)
        applications = ApplicationService.get_applications(user_id)

        export = {
            "user": {
                "email": st.session_state.get("user_email"),
                "phone": st.session_state.get("user_phone"),
                "display_name": st.session_state.get("display_name"),
            },
            "resumes": resumes,
            "interview_answers": answers,
            "job_applications": applications,
        }
        json_str = json.dumps(export, ensure_ascii=False, indent=2)
        st.download_button(
            "下载 JSON 文件",
            json_str,
            file_name="quickhire_data.json",
            mime="application/json",
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title" style="color:#EF4444;">⚠️ 危险操作</div>', unsafe_allow_html=True)
    st.warning("账号注销后，所有数据将被删除且无法恢复。")

    with st.expander("确认注销账号"):
        st.markdown("请输入 **确认注销** 以继续：")
        confirm_text = st.text_input("确认操作", key="delete_confirm")
        if st.button("永久注销我的账号", type="primary"):
            if confirm_text == "确认注销":
                st.error("此功能暂未开放，请联系管理员处理")
            else:
                st.warning("请输入正确的确认文字")

    st.markdown('</div>', unsafe_allow_html=True)
