import streamlit as st
import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from auth_service import AuthService, AuthError

st.set_page_config(
    page_title="登录 - 快克简历优化",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}

    html, body, .stMarkdown, .stText, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox div {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, #F0FDFA 0%, #ECFDF5 100%);
    }

    .topnav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 2rem;
        margin-bottom: 2rem;
        background: #FFFFFF;
        border-bottom: 1px solid #CCFBF1;
        box-shadow: 0 1px 4px rgba(15, 118, 110, 0.04);
    }
    .topnav-brand {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 1.1rem; font-weight: 700; color: #0F766E;
    }
    .topnav-link {
        color: #0D9488; font-size: 0.85rem; font-weight: 600;
        text-decoration: none; padding: 0.4rem 1rem;
        border: 1.5px solid #0D9488; border-radius: 8px;
        transition: all 0.2s ease;
    }
    .topnav-link:hover { background: #0D9488; color: #FFF; }

    .brand-hero {
        font-family: 'DM Sans', sans-serif; font-size: 2rem;
        font-weight: 700; color: #0F766E; text-align: center; margin-bottom: 0.5rem;
    }
    .brand-subtitle {
        font-size: 1rem; color: #0D9488; text-align: center; margin-bottom: 2rem;
    }

    .login-card {
        background: #FFF; border-radius: 16px; padding: 2rem 1.8rem;
        border: 1px solid #CCFBF1;
        box-shadow: 0 4px 24px rgba(15, 118, 110, 0.06);
    }
    .login-title {
        font-family: 'DM Sans', sans-serif; font-size: 1.3rem;
        font-weight: 700; color: #0F766E; margin-bottom: 1.2rem; text-align: center;
    }

    .st-key-btn_login button, .st-key-btn_register button {
        background: linear-gradient(135deg, #0D9488 0%, #059669 100%) !important;
        border: none !important; color: #FFF !important;
        font-weight: 600 !important; border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .st-key-btn_login button:hover, .st-key-btn_register button:hover {
        box-shadow: 0 6px 22px rgba(13, 148, 136, 0.4) !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ── Top Nav ──
st.markdown("""
<div class="topnav">
    <div class="topnav-brand">
        <span style="font-size:1.5rem;">📝</span>
        <span>快克简历优化</span>
    </div>
    <div>
        <a href="/app" target="_self" class="topnav-link">🏠 返回首页</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Redirect if logged in
if AuthService.is_logged_in():
    st.success("您已登录，正在跳转首页...")
    st.switch_page("app.py")

# ── Main ──
st.markdown('<div class="brand-hero">欢迎使用快克简历优化</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">登录或注册以解锁全部功能</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔑 登录</div>', unsafe_allow_html=True)
    credential = st.text_input("邮箱或手机号", placeholder="请输入邮箱或手机号", key="login_credential")
    password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
    if st.button("登 录", type="primary", use_container_width=True, key="btn_login"):
        if not credential or not password:
            st.error("请输入账号和密码")
        else:
            try:
                user = AuthService.login(credential, password)
                AuthService.set_session(user)
                st.success("登录成功！正在跳转...")
                st.switch_page("app.py")
            except AuthError as e:
                st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">📝 注册</div>', unsafe_allow_html=True)
    email = st.text_input("邮箱", placeholder="选填", key="reg_email")
    phone = st.text_input("手机号", placeholder="选填", key="reg_phone")
    name = st.text_input("昵称", placeholder="您的称呼", key="reg_name")
    pw = st.text_input("密码", type="password", placeholder="至少6位", key="reg_password")
    pw2 = st.text_input("确认密码", type="password", placeholder="请再次输入密码", key="reg_confirm")
    if st.button("注 册", type="primary", use_container_width=True, key="btn_register"):
        if not email and not phone:
            st.error("请至少填写邮箱或手机号")
        elif pw != pw2:
            st.error("两次输入的密码不一致")
        else:
            try:
                user = AuthService.register(
                    email=email.strip() or "",
                    phone=phone.strip() or "",
                    password=pw,
                    display_name=name.strip() or "",
                )
                AuthService.set_session(user)
                st.success("注册成功！正在跳转...")
                st.switch_page("app.py")
            except AuthError as e:
                st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)
