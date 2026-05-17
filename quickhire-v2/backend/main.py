from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from config import CORS_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
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


@app.get("/api/health")
def health():
    return {"status": "ok"}
