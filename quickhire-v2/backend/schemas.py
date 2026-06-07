from pydantic import BaseModel, field_validator
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str = ""
    phone: str = ""
    password: str
    display_name: str = ""

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        from config import MIN_PASSWORD_LENGTH
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"密码长度不能少于{MIN_PASSWORD_LENGTH}位")
        return v


class LoginRequest(BaseModel):
    credential: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str | None
    phone: str | None
    display_name: str | None
    job_preference: str | None = None
    city: str | None = None
    target_city: str | None = None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Resume ────────────────────────────────────────────────────
class OptimizeRequest(BaseModel):
    resume_text: str
    target_position: str
    optimization_style: str = "简洁专业"

    @field_validator("target_position")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("目标岗位不能为空")
        return v.strip()


class DiagnoseRequest(BaseModel):
    resume_text: str
    target_position: str = ""


class QuickScanRequest(BaseModel):
    resume_text: str


class InterviewQuestionRequest(BaseModel):
    resume_text: str
    difficulty: str = "中等"
    question_types: list[str] = ["简答题", "项目手撕题"]
    scope: str = "全题型混合"
    question_count: int = 5


class ResumeHistoryItem(BaseModel):
    id: int
    version_number: int
    original_content: str
    optimized_content: str | None
    target_position: str | None
    optimization_style: str | None
    analysis_result: str | None
    is_current: bool
    created_at: str | None


# ── Interview ─────────────────────────────────────────────────
class CoachStartRequest(BaseModel):
    interview_type: str = "综合面"
    difficulty: str = "中等"
    question_count: int = 5


class AnswerSubmitRequest(BaseModel):
    question: str
    user_answer: str
    question_type: str = ""
    expected_answer_points: str = ""


class ScoreResponse(BaseModel):
    overall_score: float
    dimensions: dict
    strengths: list[str]
    weaknesses: list[str]
    improved_answer: str
    key_missing_points: list[str]
    encouragement: str


class SummaryRequest(BaseModel):
    session_qa: list[dict]


# ── Profile ───────────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_length(cls, v: str) -> str:
        from config import MIN_PASSWORD_LENGTH
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"密码长度不能少于{MIN_PASSWORD_LENGTH}位")
        return v


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None
    job_preference: str | None = None
    city: str | None = None
    target_city: str | None = None


class PreferencesRequest(BaseModel):
    preferences: dict


# ── Analytics ─────────────────────────────────────────────────
class AddApplicationRequest(BaseModel):
    company_name: str
    position: str
    status: str = "applied"
    notes: str = ""


class ApplicationResponse(BaseModel):
    id: int
    company_name: str
    position: str
    status: str
    applied_at: str | None
    notes: str | None
    created_at: str | None


# ── Email verification ─────────────────────────────────────────
class SendCodeRequest(BaseModel):
    email: str


class VerifyCodeLoginRequest(BaseModel):
    email: str
    code: str


# ── API Config ──────────────────────────────────────────────────
class TestApiRequest(BaseModel):
    api_key: str | None = None
    api_model: str | None = None
    api_base_url: str | None = None


# ── Generic ───────────────────────────────────────────────────
class MessageResponse(BaseModel):
    ok: bool = True
    message: str = ""
