import asyncio, json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import AddApplicationRequest, ApplicationResponse
from dependencies import get_db, get_current_user
from models import User
from services.application_service import ApplicationService
from utils.analytics_engine import AnalyticsEngine
from utils.api_client import call_qwen_api_with_retry
from utils.prompt_builder import build_monthly_report_prompt

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user.id
    engine = AnalyticsEngine()
    return {
        "resume_timeline": engine.resume_improvement_timeline(db, uid),
        "radar_data": engine.skill_radar_data(db, uid),
        "interview_scores": engine.interview_score_history(db, uid),
        "dimension_trends": engine.interview_dimension_trends(db, uid),
        "weak_improvements": engine.weak_area_improvement(db, uid),
        "application_funnel": engine.application_funnel(db, uid),
        "question_type_performance": engine.question_type_performance(db, uid),
        "difficulty_performance": engine.difficulty_performance(db, uid),
    }


@router.post("/applications", response_model=ApplicationResponse)
def add_application(
    req: AddApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_id = ApplicationService.add_application(
        db=db,
        user_id=current_user.id,
        company=req.company_name,
        position=req.position,
        status=req.status,
        notes=req.notes,
    )
    return {"id": app_id, **req.model_dump(), "applied_at": None, "created_at": None}


@router.get("/applications", response_model=list[ApplicationResponse])
def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApplicationService.get_applications(db, current_user.id)


@router.patch("/applications/{app_id}")
def update_application_status(
    app_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ApplicationService.update_status(db, app_id, current_user.id, status)
    return {"ok": True}


@router.post("/monthly-report")
async def generate_monthly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user.id
    engine = AnalyticsEngine()
    from services.resume_service import ResumeService
    from services.interview_service import InterviewService

    resume_progress = json.dumps(engine.resume_improvement_timeline(db, uid), ensure_ascii=False)
    interview_stats = json.dumps({
        "total": len(InterviewService.get_answers(db, uid)),
        "trends": engine.interview_dimension_trends(db, uid),
    }, ensure_ascii=False)
    weak_area_progress = json.dumps(engine.weak_area_improvement(db, uid), ensure_ascii=False)
    application_funnel = json.dumps(engine.application_funnel(db, uid), ensure_ascii=False)

    prompt = build_monthly_report_prompt(
        user_name=current_user.display_name or "用户",
        resume_progress=resume_progress,
        interview_stats=interview_stats,
        weak_area_progress=weak_area_progress,
        application_funnel=application_funnel,
    )
    from services.user_settings_service import UserSettingsService
    prefs = UserSettingsService.get_preferences(db, uid)
    api_key = prefs.get("api_key")

    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key
    )
    return {"report_text": raw}
