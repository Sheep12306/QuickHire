from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent

# ── API ─────────────────────────────────────────────────────────
API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
API_MODEL = os.getenv("API_MODEL", "qwen-plus")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))

# ── Database ──────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'quickhire.db'}")

# ── JWT ───────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "quickhire-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("SESSION_EXPIRY_HOURS", "24")) * 60

# ── Encryption ───────────────────────────────────────────────
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# ── Auth ──────────────────────────────────────────────────────
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))

# ── CORS ──────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# ── Email (SMTP) ─────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ── Domain constants ──────────────────────────────────────────
RESUME_OPTIMIZATION_STYLES = ["简洁专业", "突出业绩", "技术导向", "创新风格"]
INTERVIEW_DIFFICULTIES = ["入门", "基础", "中等", "面试高频", "深度深挖"]
INTERVIEW_QUESTION_TYPES = ["选择题", "简答题", "项目手撕题", "场景面试题", "压力面试题"]
INTERVIEW_SCOPES = ["仅技术面试", "仅HR面试", "全题型混合"]
