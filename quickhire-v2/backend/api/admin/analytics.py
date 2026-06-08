from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from dependencies import get_db, require_admin
from models import User, ResumeVersion, InterviewAnswer, ApiCallLog, JobApplication
from schemas import ConversionFunnel, RetentionData, ExportReportRequest
import io
import csv

router = APIRouter()


@router.get("/conversion-funnel")
def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    since = (datetime.utcnow() - timedelta(days=days)).date()

    registered = db.query(func.count(User.id)).filter(
        func.date(User.created_at) >= since
    ).scalar() or 0

    uploaded_resume = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
        func.date(ResumeVersion.created_at) >= since
    ).scalar() or 0

    optimized = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
        func.date(ResumeVersion.created_at) >= since,
        ResumeVersion.optimized_content.isnot(None),
    ).scalar() or 0

    interviewed = db.query(func.count(func.distinct(InterviewAnswer.user_id))).filter(
        func.date(InterviewAnswer.created_at) >= since
    ).scalar() or 0

    applied = db.query(func.count(func.distinct(JobApplication.user_id))).filter(
        func.date(JobApplication.created_at) >= since
    ).scalar() or 0

    return ConversionFunnel(
        registered=registered,
        uploaded_resume=uploaded_resume,
        optimized=optimized,
        interviewed=interviewed,
        applied=applied,
    ).model_dump()


@router.get("/retention")
def get_retention(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    """Calculate week-over-week retention for last 4 weeks."""
    today = date.today()
    results = []

    for week_offset in range(4, 0, -1):
        cohort_start = today - timedelta(weeks=week_offset)
        cohort_end = cohort_start + timedelta(days=6)

        # Users who registered in this week
        cohort = db.query(User.id).filter(
            func.date(User.created_at) >= cohort_start,
            func.date(User.created_at) <= cohort_end,
        ).all()
        cohort_ids = [r[0] for r in cohort]
        cohort_size = len(cohort_ids)

        if cohort_size == 0:
            results.append(RetentionData(
                cohort=cohort_start.isoformat(),
                size=0, day1=0, day7=0, day30=0,
            ).model_dump())
            continue

        # Day-1 retention: used resume feature within 1 day of registration
        day1_count = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
            ResumeVersion.user_id.in_(cohort_ids),
            func.date(ResumeVersion.created_at) >= cohort_start,
            func.date(ResumeVersion.created_at) <= cohort_end + timedelta(days=1),
        ).scalar() or 0

        # Day-7 retention: used any feature within 7 days
        day7_count = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
            ResumeVersion.user_id.in_(cohort_ids),
            func.date(ResumeVersion.created_at) >= cohort_start,
            func.date(ResumeVersion.created_at) <= cohort_end + timedelta(days=7),
        ).scalar() or 0

        # Day-30 retention
        day30_count = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
            ResumeVersion.user_id.in_(cohort_ids),
            func.date(ResumeVersion.created_at) >= cohort_start,
            func.date(ResumeVersion.created_at) <= cohort_end + timedelta(days=30),
        ).scalar() or 0

        results.append(RetentionData(
            cohort=cohort_start.isoformat(),
            size=cohort_size,
            day1=round(day1_count / cohort_size * 100, 1),
            day7=round(day7_count / cohort_size * 100, 1),
            day30=round(day30_count / cohort_size * 100, 1),
        ).model_dump())

    return {"items": results}


@router.get("/feature-usage-heatmap")
def get_feature_usage_heatmap(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    """Return hourly feature usage data for heatmap rendering."""
    since = datetime.utcnow() - timedelta(days=days)

    rows = db.query(
        func.date(ApiCallLog.created_at).label("d"),
        func.strftime("%H", ApiCallLog.created_at).label("h"),
        func.count(ApiCallLog.id).label("cnt"),
    ).filter(
        ApiCallLog.created_at >= since
    ).group_by(text("d"), text("h")).all()

    # Build heatmap data: array of [date, hour, count]
    data = [[r.d, int(r.h), r.cnt] for r in rows]

    return {"items": data, "days": days}


@router.post("/export-report")
def export_report(
    req: ExportReportRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    """Export analytics data as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)

    date_from = req.date_from or (date.today() - timedelta(days=30)).isoformat()
    date_to = req.date_to or date.today().isoformat()

    for metric in req.metrics:
        writer.writerow([f"--- {metric} ---"])
        if metric == "users":
            writer.writerow(["ID", "邮箱", "昵称", "角色", "注册时间"])
            users = db.query(User).filter(
                func.date(User.created_at) >= date_from,
                func.date(User.created_at) <= date_to,
            ).all()
            for u in users:
                writer.writerow([u.id, u.email or "", u.display_name or "", u.role,
                                 u.created_at.isoformat() if u.created_at else ""])
        elif metric == "resumes":
            writer.writerow(["ID", "用户ID", "目标岗位", "优化风格", "创建时间"])
            resumes = db.query(ResumeVersion).filter(
                func.date(ResumeVersion.created_at) >= date_from,
                func.date(ResumeVersion.created_at) <= date_to,
            ).all()
            for r in resumes:
                writer.writerow([r.id, r.user_id, r.target_position, r.optimization_style,
                                 r.created_at.isoformat() if r.created_at else ""])
        elif metric == "api_calls":
            writer.writerow(["ID", "用户ID", "模型", "Token数", "耗时ms", "状态", "成本", "时间"])
            calls = db.query(ApiCallLog).filter(
                func.date(ApiCallLog.created_at) >= date_from,
                func.date(ApiCallLog.created_at) <= date_to,
            ).all()
            for c in calls:
                tokens = (c.prompt_tokens or 0) + (c.completion_tokens or 0)
                writer.writerow([c.id, c.user_id, c.model, tokens, c.latency_ms,
                                 c.status, c.cost, c.created_at.isoformat() if c.created_at else ""])
        writer.writerow([])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{date.today().isoformat()}.csv"},
    )


