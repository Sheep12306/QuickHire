import asyncio, json, io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from schemas import (
    OptimizeRequest, DiagnoseRequest, QuickScanRequest,
    InterviewQuestionRequest, ResumeHistoryItem,
)
from dependencies import get_db, get_current_user, get_optional_user
from models import User
from services.resume_service import ResumeService
from services.interview_service import InterviewService
from utils.api_client import call_qwen_api_with_retry, safe_json_parse
from utils.prompt_builder import (
    build_optimize_prompt,
    build_resume_diagnosis_prompt,
    build_interview_question_prompt,
)
from utils.resume_parser import parse_resume_text, resume_to_summary
from utils.defect_detector import ResumeDefectDetector
from utils.file_parser import parse_uploaded_file

router = APIRouter()


import re

def _split_ai_result(raw: str) -> dict:
    """Split AI response into comparison, hr_review, and clean optimized resume.
    AI output order: 【简历诊断】→【优化后简历】→ resume →【优化对比】→【HR视角点评】"""
    optimized = raw
    comparison = ""
    hr_review = ""

    # Step 1: Split at 【优化后简历】— everything after is the resume + trailing meta
    opt_markers = ["【优化后简历】", "【优化后】", "【优化简历】", "【简历正文】"]
    for marker in opt_markers:
        if marker in raw:
            parts = raw.split(marker, 1)
            optimized = parts[1]  # resume + comparison + hr_review
            break

    # Step 2: Split off 【优化对比】from optimized (it comes AFTER the resume)
    comp_markers = ["【优化对比】", "【改进说明】", "【优化分析】"]
    for marker in comp_markers:
        if marker in optimized:
            opt_parts = optimized.split(marker, 1)
            optimized = opt_parts[0]
            comparison = opt_parts[1]
            break

    # Step 3: Split off 【HR视角点评】from comparison (it comes AFTER comparison)
    hr_markers = ["【HR视角点评】", "【HR点评】", "【HR建议】"]
    for marker in hr_markers:
        if marker in comparison:
            hr_parts = comparison.split(marker, 1)
            comparison = hr_parts[0]
            hr_review = hr_parts[1]
            break

    # Also check if HR review is in optimized (in case comparison wasn't found)
    if not hr_review:
        for marker in hr_markers:
            if marker in optimized:
                hr_parts = optimized.split(marker, 1)
                optimized = hr_parts[0]
                hr_review = hr_parts[1]
                break

    # Clean up
    optimized = optimized.strip()
    optimized = re.sub(r'\n{3,}', '\n\n', optimized)
    comparison = comparison.strip()
    hr_review = hr_review.strip()

    return {
        "optimized_text": optimized,
        "comparison": comparison,
        "hr_review": hr_review,
    }


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    text = parse_uploaded_file(file.filename, content)
    return {
        "filename": file.filename,
        "content": text,
        "char_count": len(text),
    }


@router.post("/optimize")
async def optimize_resume(
    req: OptimizeRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    prompt = build_optimize_prompt(
        resume_text=req.resume_text,
        target_position=req.target_position,
        optimization_style=req.optimization_style,
    )
    # Get per-user API key or fall back to config default
    api_key = None
    if current_user:
        from services.user_settings_service import UserSettingsService
        prefs = UserSettingsService.get_preferences(db, current_user.id)
        api_key = prefs.get("api_key")

    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key
    )
    parts = _split_ai_result(raw)

    result = {
        "optimized_text": parts["optimized_text"],
        "comparison": parts["comparison"],
        "hr_review": parts["hr_review"],
    }

    if current_user:
        version_id = ResumeService.save_resume(
            db=db,
            user_id=current_user.id,
            original_content=req.resume_text,
            optimized_content=parts["optimized_text"],
            target_position=req.target_position,
            optimization_style=req.optimization_style,
            analysis_result=parts["comparison"] + "\n\n" + parts["hr_review"],
        )
        result["saved_version_id"] = version_id

    return result


@router.post("/diagnose")
async def diagnose_resume(
    req: DiagnoseRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    prompt = build_resume_diagnosis_prompt(
        resume_text=req.resume_text,
        target_position=req.target_position,
    )
    api_key = None
    if current_user:
        from services.user_settings_service import UserSettingsService
        prefs = UserSettingsService.get_preferences(db, current_user.id)
        api_key = prefs.get("api_key")

    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key
    )
    result = safe_json_parse(raw)

    if current_user:
        ResumeService.update_analysis(db, current_user.id, json.dumps(result, ensure_ascii=False))

    return result


@router.post("/quick-scan")
def quick_scan(req: QuickScanRequest):
    detector = ResumeDefectDetector()
    defects = detector.detect_all_defects(req.resume_text)
    severity = detector.get_severity_summary(defects)
    suggestions = detector.generate_optimization_suggestions(req.resume_text)
    score = max(30, 100 - severity["high"] * 15 - severity["medium"] * 8 - severity["low"] * 3)
    return {
        "defects": defects,
        "severity_summary": severity,
        "suggestions": suggestions,
        "overall_score": score,
    }


@router.post("/questions")
async def generate_questions(
    req: InterviewQuestionRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    parsed = parse_resume_text(req.resume_text)
    summary = resume_to_summary(parsed)
    technical_stack = parsed.get("skills", {}).get("technical", [])
    project_highlights = [
        f"{p.get('name', p.get('title', ''))}: {p.get('description', '')}"
        for p in parsed.get("projects", [])
    ]

    api_key = None
    if current_user:
        from services.user_settings_service import UserSettingsService
        prefs = UserSettingsService.get_preferences(db, current_user.id)
        api_key = prefs.get("api_key")

    prompt = build_interview_question_prompt(
        resume_summary=summary,
        technical_stack=technical_stack,
        project_highlights=project_highlights,
        difficulty=req.difficulty,
        question_types=req.question_types,
        scope=req.scope,
        question_count=req.question_count,
    )
    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key
    )
    result = safe_json_parse(raw)

    questions = result.get("questions", []) if isinstance(result, dict) else []
    if current_user:
        InterviewService.save_question_bank(
            db=db,
            user_id=current_user.id,
            questions_json=json.dumps(questions, ensure_ascii=False),
            difficulty=req.difficulty,
            question_types=",".join(req.question_types),
            scope=req.scope,
            question_count=len(questions),
        )

    return {"questions": questions}


@router.get("/history", response_model=list[ResumeHistoryItem])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ResumeService.get_resume_history(db, current_user.id)


@router.get("/latest")
def get_latest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = ResumeService.get_latest_resume(db, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="No resume found")
    return result


from fastapi.responses import StreamingResponse
from urllib.parse import quote
from utils.export_utils import generate_pdf_resume, TEMPLATES


@router.post("/export-pdf")
async def export_pdf(
    template_id: int = Form(...),
    content: str = Form(...),
    page_limit: int | None = Form(None),
    photo: UploadFile | None = File(None),
):
    """Generate a PDF resume with template selection and optional photo."""
    photo_bytes = None
    if photo:
        photo_bytes = await photo.read()

    try:
        pdf_bytes = await asyncio.to_thread(
            generate_pdf_resume,
            content=content,
            template_id=template_id,
            page_limit=page_limit,
            photo_bytes=photo_bytes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    filename = "resume.pdf"
    # Use candidate name if we can extract it (ASCII-safe fallback)
    first_line = content.split("\n")[0].strip() if content else ""
    name_match = re.match(r"^([^\s|｜]+)", first_line)
    if name_match:
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "", name_match.group(1))
        if safe_name:
            filename = f"{safe_name}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/templates")
def list_templates():
    """Return available PDF templates info."""
    return [
        {"id": tid, "name": name, "description": desc}
        for tid, (name, desc, _fn) in TEMPLATES.items()
    ]


@router.patch("/{resume_id}/set-current")
def set_current(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ResumeService.set_current_version(db, current_user.id, resume_id)
    return {"ok": True}
