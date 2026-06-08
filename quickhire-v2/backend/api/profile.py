import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from schemas import (
    ChangePasswordRequest, ProfileUpdateRequest,
    PreferencesRequest, TestApiRequest, UserResponse, MessageResponse,
)
from dependencies import get_db, get_current_user, get_current_user_allow_pw_change
from models import User
from services.user_settings_service import UserSettingsService
from services.resume_service import ResumeService
from services.interview_service import InterviewService
from services.application_service import ApplicationService
from utils.api_client import call_qwen_api_with_retry, test_api_connection
from utils.file_parser import parse_uploaded_file

router = APIRouter()


@router.get("/preferences")
def get_preferences(
    current_user: User = Depends(get_current_user_allow_pw_change),
    db: Session = Depends(get_db),
):
    return UserSettingsService.get_preferences(db, current_user.id)


@router.put("/preferences")
def save_preferences(
    req: PreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    UserSettingsService.save_preferences(db, current_user.id, req.preferences)
    return {"ok": True}


@router.patch("/password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_allow_pw_change),
    db: Session = Depends(get_db),
):
    try:
        UserSettingsService.change_password(
            db, current_user.id, req.old_password, req.new_password
        )
        if current_user.must_change_password:
            current_user.must_change_password = False
            db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


@router.patch("/info")
def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    UserSettingsService.update_profile(
        db,
        current_user.id,
        display_name=req.display_name,
        email=req.email,
        phone=req.phone,
        job_preference=req.job_preference,
        city=req.city,
        target_city=req.target_city,
    )
    return {"ok": True}


@router.get("/export")
def export_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user.id
    return {
        "user": {
            "email": current_user.email,
            "phone": current_user.phone,
            "display_name": current_user.display_name,
            "job_preference": current_user.job_preference,
            "city": current_user.city,
            "target_city": current_user.target_city,
        },
        "resumes": ResumeService.get_resume_history(db, uid),
        "interviews": InterviewService.get_answers(db, uid),
        "applications": ApplicationService.get_applications(db, uid),
        "question_banks": InterviewService.get_question_banks(db, uid),
    }


@router.post("/test-api")
def test_api(
    req: TestApiRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from services.user_settings_service import UserSettingsService
    prefs = UserSettingsService.get_preferences(db, current_user.id)
    key = req.api_key or prefs.get("api_key")
    model = req.api_model or prefs.get("api_model")
    base_url = req.api_base_url or prefs.get("api_base_url")
    return test_api_connection(api_key=key, api_model=model, api_base_url=base_url)


@router.put("/api-config")
def save_api_config(
    req: PreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = UserSettingsService.get_preferences(db, current_user.id)
    if "api_key" in req.preferences:
        prefs["api_key"] = req.preferences["api_key"]
    if "api_model" in req.preferences:
        prefs["api_model"] = req.preferences["api_model"]
    if "api_base_url" in req.preferences:
        prefs["api_base_url"] = req.preferences["api_base_url"]
    UserSettingsService.save_preferences(db, current_user.id, prefs)
    return {"ok": True}


@router.get("/usage")
def get_usage(
    current_user: User = Depends(get_current_user_allow_pw_change),
    db: Session = Depends(get_db),
):
    from services.user_settings_service import UserSettingsService
    from services.usage_service import UsageService
    prefs = UserSettingsService.get_preferences(db, current_user.id)
    has_own_key = bool(prefs.get("api_key"))
    return UsageService.get_remaining(db, current_user.id, has_own_key)


@router.get("/api-config")
def get_api_config(
    current_user: User = Depends(get_current_user_allow_pw_change),
    db: Session = Depends(get_db),
):
    prefs = UserSettingsService.get_preferences(db, current_user.id)
    return {
        "api_key": bool(prefs.get("api_key")),
        "api_model": prefs.get("api_model", ""),
        "api_base_url": prefs.get("api_base_url", ""),
    }
