import asyncio, json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import CoachStartRequest, AnswerSubmitRequest, ScoreResponse, SummaryRequest
from dependencies import get_db, get_current_user
from models import User
from services.resume_service import ResumeService
from services.interview_service import InterviewService
from utils.api_client import call_qwen_api_with_retry, safe_json_parse
from utils.prompt_builder import (
    build_interview_coach_prompt,
    build_answer_scoring_prompt,
    build_interview_summary_prompt,
    build_weakness_reinforcement_prompt,
)
from utils.resume_parser import parse_resume_text, resume_to_summary

router = APIRouter()


def _get_user_api_config(db: Session, user: User) -> tuple[str | None, str | None, str | None]:
    from services.user_settings_service import UserSettingsService
    prefs = UserSettingsService.get_preferences(db, user.id)
    return prefs.get("api_key"), prefs.get("api_model"), prefs.get("api_base_url")


@router.post("/coach/start")
async def coach_start(
    req: CoachStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    latest = ResumeService.get_latest_resume(db, current_user.id)
    resume_text = latest.get("original_content", "") if latest else ""

    # Get weak areas from past answers
    answers = InterviewService.get_answers(db, current_user.id)
    weak_areas = []
    for a in answers[-10:]:
        if a.get("ai_feedback"):
            try:
                fb = json.loads(a["ai_feedback"])
                weak_areas.extend(fb.get("weaknesses", []))
            except (json.JSONDecodeError, TypeError):
                pass
    weak_areas = list(set(weak_areas))[:5]

    if resume_text:
        parsed = parse_resume_text(resume_text)
        summary = resume_to_summary(parsed)
        technical_stack = parsed.get("skills", {}).get("technical", [])
    else:
        summary = "未上传简历"
        technical_stack = []

    prompt = build_interview_coach_prompt(
        resume_summary=summary,
        technical_stack=technical_stack,
        weak_areas=weak_areas,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        question_count=req.question_count,
    )

    api_key, api_model, api_base_url = _get_user_api_config(db, current_user)
    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key, api_model=api_model, api_base_url=api_base_url
    )
    result = safe_json_parse(raw)
    questions = result.get("questions", []) if isinstance(result, dict) else []

    return {"questions": questions}


@router.post("/coach/score")
async def coach_score(
    req: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = build_answer_scoring_prompt(
        question_text=req.question,
        expected_answer_points=req.expected_answer_points,
        user_answer=req.user_answer,
        question_type=req.question_type,
    )
    api_key, api_model, api_base_url = _get_user_api_config(db, current_user)
    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key, api_model=api_model, api_base_url=api_base_url
    )
    result = safe_json_parse(raw)

    if isinstance(result, dict):
        InterviewService.save_answer(
            db=db,
            user_id=current_user.id,
            question_text=req.question,
            user_answer=req.user_answer,
            ai_score=result.get("overall_score", 0),
            ai_feedback=json.dumps(result, ensure_ascii=False),
        )

    return result


@router.post("/coach/summary")
async def coach_summary(
    req: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prompt = build_interview_summary_prompt(session_data=req.session_qa)
    api_key, api_model, api_base_url = _get_user_api_config(db, current_user)
    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key, api_model=api_model, api_base_url=api_base_url
    )
    return safe_json_parse(raw)


@router.post("/reinforcement")
async def reinforcement(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    answers = InterviewService.get_answers(db, current_user.id)
    weak_areas = []
    for a in answers:
        if a.get("ai_feedback"):
            try:
                fb = json.loads(a["ai_feedback"])
                for dim, data in fb.get("dimensions", {}).items():
                    if data.get("score", 100) < 60:
                        weak_areas.append(dim)
            except (json.JSONDecodeError, TypeError):
                pass

    low_score_dimensions = list(set(weak_areas))  # same extraction, different label
    weak_areas = low_score_dimensions

    if not weak_areas:
        return {"questions": [], "message": "暂无弱项需要强化训练"}

    # Get resume summary for context
    from services.resume_service import ResumeService
    from utils.resume_parser import parse_resume_text, resume_to_summary
    latest = ResumeService.get_latest_resume(db, current_user.id)
    resume_summary = "未上传简历"
    if latest and latest.get("original_content"):
        parsed = parse_resume_text(latest["original_content"])
        resume_summary = resume_to_summary(parsed)

    prompt = build_weakness_reinforcement_prompt(
        weak_areas=weak_areas,
        low_score_dimensions=low_score_dimensions,
        resume_summary=resume_summary,
        question_count=5,
    )
    api_key, api_model, api_base_url = _get_user_api_config(db, current_user)
    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key, api_model=api_model, api_base_url=api_base_url
    )
    result = safe_json_parse(raw)
    questions = result.get("questions", []) if isinstance(result, dict) else []
    return {"questions": questions}


@router.get("/answers")
def get_answers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InterviewService.get_answers(db, current_user.id)


@router.get("/question-banks")
def get_question_banks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return InterviewService.get_question_banks(db, current_user.id)
