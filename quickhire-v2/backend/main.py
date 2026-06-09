from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from config import CORS_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        import logging
        logging.error(f"init_db failed: {e}")
    yield


app = FastAPI(
    title="QuickHire API",
    description="AI简历优化 & 面试教练 后端服务",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Import and register routers ──────────────────────────────
from api.auth import router as auth_router
from api.resume import router as resume_router
from api.interview import router as interview_router
from api.analytics import router as analytics_router
from api.profile import router as profile_router
from api.practice import router as practice_router

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview_router, prefix="/api/interview", tags=["Interview"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(practice_router, prefix="/api/practice", tags=["Practice"])

from api.admin import admin_router
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


@app.get("/api/health")
def health():
    from database import SessionLocal
    from models import User, SystemConfig
    info = {"status": "ok", "db": "ok", "admin_exists": False, "system_api_key": False}
    try:
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.role == "super_admin").first()
            info["admin_exists"] = bool(admin)
            info["admin_email"] = admin.email if admin else None
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_key").first()
            info["system_api_key"] = bool(cfg and cfg.value)
        finally:
            db.close()
    except Exception as e:
        info["db"] = f"error: {e}"
        info["status"] = "degraded"
    return info
