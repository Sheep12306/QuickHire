from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
API_MODEL = os.getenv("API_MODEL", "qwen-plus")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))

# ── Database ──────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'quickhire.db'}")

# ── Auth ──────────────────────────────────────────────────────
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "6"))

STREAMLIT_CONFIG = {
    "page_title": "AI简历优化&面试题生成系统",
    "page_icon": "📝",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

RESUME_OPTIMIZATION_STYLES = [
    "简洁专业",
    "突出业绩",
    "技术导向",
    "创新风格"
]

INTERVIEW_DIFFICULTIES = [
    "入门",
    "基础",
    "中等",
    "面试高频",
    "深度深挖"
]

INTERVIEW_QUESTION_TYPES = [
    "选择题",
    "简答题",
    "项目手撕题",
    "场景面试题",
    "压力面试题"
]

INTERVIEW_SCOPES = [
    "仅技术面试",
    "仅HR面试",
    "全题型混合"
]