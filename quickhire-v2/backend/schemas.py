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
    role: str = "user"
    is_active: bool = True
    banned_until: datetime | None = None
    ban_reason: str | None = None
    membership_type: str = "free"
    membership_expires_at: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

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


# ── Admin ─────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list


class DashboardOverview(BaseModel):
    total_users: int = 0
    new_users_today: int = 0
    active_users_7d: int = 0
    total_resumes: int = 0
    optimizations_today: int = 0
    total_optimizations: int = 0
    ai_calls_today: int = 0
    error_rate: float = 0.0


class TrendItem(BaseModel):
    date: str
    registrations: int = 0
    optimizations: int = 0
    api_calls: int = 0


class AlertItem(BaseModel):
    level: str
    message: str
    time: str


class FeatureRanking(BaseModel):
    name: str
    count: int
    percentage: float


class AdminUserListItem(BaseModel):
    id: int
    email: str | None
    phone: str | None
    display_name: str | None
    role: str
    is_active: bool
    membership_type: str
    resume_count: int = 0
    created_at: str | None
    last_login_at: str | None


class AdminUserDetail(BaseModel):
    id: int
    email: str | None
    phone: str | None
    display_name: str | None
    job_preference: str | None
    city: str | None
    target_city: str | None
    role: str
    is_active: bool
    banned_until: str | None
    ban_reason: str | None
    membership_type: str
    membership_expires_at: str | None
    last_login_at: str | None
    created_at: str | None
    updated_at: str | None
    resume_count: int = 0
    interview_count: int = 0
    optimize_count: int = 0


class BanUserRequest(BaseModel):
    reason: str = ""
    duration_hours: int = 0  # 0 = permanent


class ChangeRoleRequest(BaseModel):
    role: str


class AdminUserNoteRequest(BaseModel):
    note: str


class AdminUserNoteResponse(BaseModel):
    id: int
    admin_id: int
    admin_name: str = ""
    note: str
    created_at: str | None


class AdminResumeListItem(BaseModel):
    id: int
    user_id: int
    user_email: str = ""
    user_name: str = ""
    original_content: str
    optimized_content: str | None
    target_position: str | None
    optimization_style: str | None
    version_number: int
    is_current: bool
    flagged: bool = False
    flag_reason: str | None = None
    created_at: str | None


class FlagResumeRequest(BaseModel):
    flagged: bool
    flag_reason: str = ""


class ApiCallLogItem(BaseModel):
    id: int
    user_id: int | None
    user_email: str = ""
    endpoint: str | None
    model: str | None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int | None
    status: str
    error_message: str | None
    cost: float = 0.0
    created_at: str | None


class CostStatsResponse(BaseModel):
    total_cost: float
    total_calls: int
    total_tokens: int
    by_model: list[dict]
    daily: list[dict]


class RateLimitConfig(BaseModel):
    max_per_day: int = 2
    max_per_hour: int = 10
    cooldown_minutes: int = 1


class ConversionFunnel(BaseModel):
    registered: int = 0
    uploaded_resume: int = 0
    optimized: int = 0
    interviewed: int = 0
    applied: int = 0


class RetentionData(BaseModel):
    cohort: str
    size: int
    day1: float = 0
    day7: float = 0
    day30: float = 0


class ExportReportRequest(BaseModel):
    metrics: list[str]
    format: str = "csv"
    date_from: str = ""
    date_to: str = ""


class AdminConfigItem(BaseModel):
    key: str
    value: str | None
    description: str = ""


class ResumeTemplateRequest(BaseModel):
    name: str
    description: str = ""
    template_content: str = ""
    thumbnail_url: str = ""
    category: str = ""
    is_active: bool = True
    sort_order: int = 0


class PromptTemplateRequest(BaseModel):
    name: str
    template_type: str
    content: str
    variables: str = ""
    is_default: bool = False
    is_active: bool = True


class AnnouncementRequest(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    is_published: bool = False
    published_at: str | None = None
    expires_at: str | None = None


class HelpArticleRequest(BaseModel):
    title: str
    content: str
    category: str = ""
    tags: str = ""
    sort_order: int = 0
    is_published: bool = False


class PackageRequest(BaseModel):
    name: str
    description: str = ""
    price: float = 0.0
    duration_days: int = 30
    optimize_limit: int = 10
    diagnose_limit: int = 10
    is_active: bool = True
    sort_order: int = 0


class OrderRefundRequest(BaseModel):
    reason: str = ""


class ResetPasswordRequest(BaseModel):
    new_password: str


class IpWhitelistRequest(BaseModel):
    ips: list[str]
    enabled: bool = False


class RolePermission(BaseModel):
    role: str
    label: str
    permissions: list[str]
