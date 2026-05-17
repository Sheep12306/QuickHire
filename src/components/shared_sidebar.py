import streamlit as st
from auth_service import AuthService
from api_config import is_api_configured


def render_shared_sidebar(current_page: str = "home"):
    # Narrow sidebar + tighter spacing
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                width: 210px !important;
                min-width: 200px !important;
                max-width: 220px !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                margin-bottom: 0.2rem !important;
            }
            [data-testid="stSidebar"] hr {
                margin: 0.5rem 0 !important;
            }
            [data-testid="stSidebar"] .stButton button {
                padding: 0.3rem 0.6rem !important;
                font-size: 0.75rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # ── Brand header ──
        st.markdown("""
            <div style="padding:0.25rem 0 0.75rem 0;text-align:center;">
                <div style="font-size:1.15rem;font-weight:700;color:#FFFFFF;line-height:1.3;">
                    📝 快克简历优化
                </div>
                <div style="font-size:0.68rem;color:#5EEAD4;margin-top:0.15rem;">
                    AI 简历优化 & 面试教练
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── User section ──
        if AuthService.is_logged_in():
            display_name = st.session_state.get("display_name", "用户")
            email = st.session_state.get("user_email") or ""
            phone = st.session_state.get("user_phone") or ""
            account = email or phone or ""

            st.markdown(f"""
                <div style="background:rgba(255,255,255,0.08);border-radius:10px;
                            padding:0.6rem 0.75rem;margin-bottom:0.5rem;text-align:center;">
                    <div style="width:36px;height:36px;border-radius:50%;
                                background:linear-gradient(135deg,#5EEAD4,#0D9488);
                                color:#FFF;font-size:1rem;font-weight:700;
                                display:inline-flex;align-items:center;justify-content:center;
                                margin-bottom:0.3rem;">
                        {display_name[0].upper() if display_name else "?"}
                    </div>
                    <div style="font-size:0.82rem;font-weight:600;color:#FFFFFF;">
                        {display_name}
                    </div>
                    <div style="font-size:0.62rem;color:#99C7C3;margin-top:0.1rem;
                                overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        {account}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align:center;margin-bottom:0.5rem;">
                    <a href="/pages/01_login" target="_self"
                       style="display:inline-block;background:linear-gradient(135deg,#5EEAD4,#0D9488);
                              color:#FFF;padding:0.4rem 1.5rem;border-radius:8px;
                              font-size:0.8rem;font-weight:600;text-decoration:none;
                              box-shadow:0 2px 8px rgba(13,148,136,0.3);">
                        🔐 登录 / 注册
                    </a>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Nav links ──
        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/02_resume_optimizer.py", label="📝 简历优化中心")

        st.markdown("---")

        if AuthService.is_logged_in():
            st.page_link("pages/03_interview_coach.py", label="🎤 AI面试教练")
            st.page_link("pages/04_analytics.py", label="📊 数据看板")
            st.page_link("pages/05_profile.py", label="⚙️ 个人中心")

            st.markdown("---")

            if st.button("🚪 退出登录", use_container_width=True):
                AuthService.clear_session()
                st.rerun()

        # ── Core features ──
        st.markdown("""
            <div style="font-size:0.7rem;color:#99C7C3;line-height:1.6;">
                <div style="font-weight:600;color:#99F6E4;margin-bottom:0.2rem;">核心功能</div>
                · 简历智能润色<br>
                · AI 深度分析<br>
                · 面试题库生成<br>
                · AI 面试教练<br>
                · 数据看板
            </div>
        """, unsafe_allow_html=True)

        # ── Privacy ──
        st.markdown("""
            <div style="display:flex;align-items:center;gap:0.35rem;padding:0.4rem 0.6rem;
                        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);
                        border-radius:6px;font-size:0.65rem;color:#99C7C3;margin-top:0.75rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#5EEAD4" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                数据加密存储，仅你可见
            </div>
        """, unsafe_allow_html=True)

        # ── API status ──
        api_ok = is_api_configured()
        color = "#5EEAD4" if api_ok else "#F59E0B"
        text = "API 已连接" if api_ok else "⚠️ API 未配置"
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.35rem;padding:0.4rem 0.6rem;
                        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);
                        border-radius:6px;font-size:0.65rem;color:{color};margin-top:0.4rem;">
                <span style="width:6px;height:6px;border-radius:50%;background:{color};display:inline-block;"></span>
                {text}
            </div>
        """, unsafe_allow_html=True)
        if not api_ok:
            st.markdown(
                '<div style="font-size:0.6rem;color:#F59E0B;margin-top:0.2rem;">'
                '→ <a href="/pages/05_profile" target="_self" style="color:#5EEAD4;">个人中心配置 API</a></div>',
                unsafe_allow_html=True,
            )

        # ── Footer ──
        st.markdown("""
            <div style="font-size:0.65rem;color:#7AADA9;margin-top:1rem;text-align:center;line-height:1.4;">
                Powered by Streamlit & DeepSeek
            </div>
        """, unsafe_allow_html=True)
