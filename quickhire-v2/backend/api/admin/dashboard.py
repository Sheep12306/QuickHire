from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from dependencies import get_db, require_admin
from models import User, ResumeVersion, ApiCallLog
from schemas import DashboardOverview, TrendItem, AlertItem, FeatureRanking, MessageResponse

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    now = datetime.utcnow()
    today = date.today()
    today_str = today.isoformat()

    total_users = db.query(func.count(User.id)).scalar() or 0
    new_users_today = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today_str
    ).scalar() or 0

    seven_days_ago = now - timedelta(days=7)
    active_users_7d = db.query(func.count(func.distinct(ResumeVersion.user_id))).filter(
        ResumeVersion.created_at >= seven_days_ago
    ).scalar() or 0

    total_resumes = db.query(func.count(ResumeVersion.id)).scalar() or 0
    total_optimizations = db.query(func.count(ResumeVersion.id)).filter(
        ResumeVersion.optimized_content.isnot(None)
    ).scalar() or 0
    optimizations_today = db.query(func.count(ResumeVersion.id)).filter(
        ResumeVersion.optimized_content.isnot(None),
        func.date(ResumeVersion.created_at) == today_str,
    ).scalar() or 0

    ai_calls_today = db.query(func.count(ApiCallLog.id)).filter(
        func.date(ApiCallLog.created_at) == today_str
    ).scalar() or 0

    total_ai_calls = db.query(func.count(ApiCallLog.id)).scalar() or 0
    error_calls = db.query(func.count(ApiCallLog.id)).filter(
        ApiCallLog.status != "success"
    ).scalar() or 0
    error_rate = round(error_calls / total_ai_calls * 100, 2) if total_ai_calls > 0 else 0.0

    return DashboardOverview(
        total_users=total_users,
        new_users_today=new_users_today,
        active_users_7d=active_users_7d,
        total_resumes=total_resumes,
        optimizations_today=optimizations_today,
        total_optimizations=total_optimizations,
        ai_calls_today=ai_calls_today,
        error_rate=error_rate,
    )


@router.get("/trends")
def get_trends(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    results: list[TrendItem] = []
    for i in range(days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        d_str = d.isoformat()

        registrations = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == d_str
        ).scalar() or 0

        optimizations = db.query(func.count(ResumeVersion.id)).filter(
            ResumeVersion.optimized_content.isnot(None),
            func.date(ResumeVersion.created_at) == d_str,
        ).scalar() or 0

        api_calls = db.query(func.count(ApiCallLog.id)).filter(
            func.date(ApiCallLog.created_at) == d_str
        ).scalar() or 0

        results.append(TrendItem(
            date=d_str,
            registrations=registrations,
            optimizations=optimizations,
            api_calls=api_calls,
        ))

    return {"items": [r.model_dump() for r in results]}


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    alerts: list[dict] = []

    # High error rate in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    hour_calls = db.query(func.count(ApiCallLog.id)).filter(
        ApiCallLog.created_at >= one_hour_ago
    ).scalar() or 0
    hour_errors = db.query(func.count(ApiCallLog.id)).filter(
        ApiCallLog.created_at >= one_hour_ago,
        ApiCallLog.status != "success",
    ).scalar() or 0
    if hour_calls > 10 and hour_errors / hour_calls > 0.1:
        alerts.append({
            "level": "error",
            "message": f"过去1小时API错误率 {(hour_errors / hour_calls * 100):.1f}%",
            "time": datetime.utcnow().isoformat(),
        })

    # Expired memberships
    expired = db.query(func.count(User.id)).filter(
        User.membership_type != "free",
        User.membership_expires_at < datetime.utcnow(),
    ).scalar() or 0
    if expired > 0:
        alerts.append({
            "level": "warning",
            "message": f"{expired} 个付费会员已过期",
            "time": datetime.utcnow().isoformat(),
        })

    # Banned users about to expire
    soon = datetime.utcnow() + timedelta(hours=24)
    unbanned = db.query(func.count(User.id)).filter(
        User.banned_until.isnot(None),
        User.banned_until <= soon,
        User.banned_until > datetime.utcnow(),
    ).scalar() or 0
    if unbanned > 0:
        alerts.append({
            "level": "info",
            "message": f"{unbanned} 个封禁用户将在24小时内解封",
            "time": datetime.utcnow().isoformat(),
        })

    return {"items": alerts}


@router.get("/feature-ranking")
def get_feature_ranking(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    since = datetime.utcnow() - timedelta(days=days)

    # Count API calls by endpoint
    rows = db.query(
        ApiCallLog.endpoint,
        func.count(ApiCallLog.id).label("cnt")
    ).filter(
        ApiCallLog.created_at >= since
    ).group_by(ApiCallLog.endpoint).order_by(text("cnt DESC")).limit(10).all()

    label_map = {
        "optimize": "简历优化",
        "diagnose": "简历诊断",
        "quick-scan": "快速扫描",
        "questions": "面试题生成",
        "coach/start": "模拟面试",
        "coach/score": "面试评分",
    }

    total = sum(r.cnt for r in rows) or 1
    items = [
        FeatureRanking(
            name=label_map.get(r.endpoint, r.endpoint or "未知"),
            count=r.cnt,
            percentage=round(r.cnt / total * 100, 1),
        )
        for r in rows
    ]
    return {"items": [i.model_dump() for i in items]}


@router.get("/recent-activities")
def get_recent_activities(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    # Recent users
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(limit // 2).all()
    activities = [
        {
            "type": "user_registered",
            "message": f"{u.display_name or u.email} 注册了新账号",
            "user_id": u.id,
            "time": u.created_at.isoformat() if u.created_at else None,
        }
        for u in recent_users
    ]

    # Recent optimizations
    recent_opts = (
        db.query(ResumeVersion).filter(ResumeVersion.optimized_content.isnot(None))
        .order_by(ResumeVersion.created_at.desc())
        .limit(limit - len(activities))
        .all()
    )
    for r in recent_opts:
        user = db.query(User).filter(User.id == r.user_id).first()
        activities.append({
            "type": "resume_optimized",
            "message": f"{user.display_name or user.email or '用户'} 优化了简历 (目标: {r.target_position or '未指定'})",
            "user_id": r.user_id,
            "resume_id": r.id,
            "time": r.created_at.isoformat() if r.created_at else None,
        })

    activities.sort(key=lambda a: a["time"] or "", reverse=True)
    return {"items": activities[:limit]}
