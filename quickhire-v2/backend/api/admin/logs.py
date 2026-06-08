from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependencies import get_db, require_admin
from models import User, ApiCallLog, SystemConfig
from schemas import ApiCallLogItem, CostStatsResponse, RateLimitConfig, MessageResponse

router = APIRouter()


@router.get("/api-calls")
def list_api_calls(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    user_id: int = Query(None),
    model: str = Query(""),
    status: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(ApiCallLog)

    if user_id:
        q = q.filter(ApiCallLog.user_id == user_id)
    if model:
        q = q.filter(ApiCallLog.model.like(f"%{model}%"))
    if status:
        q = q.filter(ApiCallLog.status == status)
    if date_from:
        q = q.filter(func.date(ApiCallLog.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(ApiCallLog.created_at) <= date_to)

    total = q.count()
    logs = q.order_by(ApiCallLog.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        items.append(ApiCallLogItem(
            id=log.id,
            user_id=log.user_id,
            user_email=user.email if user else "",
            endpoint=log.endpoint,
            model=log.model,
            prompt_tokens=log.prompt_tokens or 0,
            completion_tokens=log.completion_tokens or 0,
            latency_ms=log.latency_ms,
            status=log.status,
            error_message=log.error_message,
            cost=log.cost or 0.0,
            created_at=log.created_at.isoformat() if log.created_at else None,
        ).model_dump())

    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/errors")
def list_errors(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    date_from: str = Query(""),
    date_to: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(ApiCallLog).filter(ApiCallLog.status != "success")
    if date_from:
        q = q.filter(func.date(ApiCallLog.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(ApiCallLog.created_at) <= date_to)

    total = q.count()
    logs = q.order_by(ApiCallLog.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = [{
        "id": log.id,
        "user_id": log.user_id,
        "endpoint": log.endpoint,
        "model": log.model,
        "status": log.status,
        "error_message": log.error_message,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    } for log in logs]

    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/cost-stats")
def get_cost_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    since = datetime.utcnow() - timedelta(days=days)

    # Overall stats
    total_cost = db.query(func.sum(ApiCallLog.cost)).filter(
        ApiCallLog.created_at >= since
    ).scalar() or 0.0

    total_calls = db.query(func.count(ApiCallLog.id)).filter(
        ApiCallLog.created_at >= since
    ).scalar() or 0

    total_tokens = db.query(
        func.sum(ApiCallLog.prompt_tokens + ApiCallLog.completion_tokens)
    ).filter(ApiCallLog.created_at >= since).scalar() or 0

    # By model
    model_rows = db.query(
        ApiCallLog.model,
        func.count(ApiCallLog.id).label("calls"),
        func.sum(ApiCallLog.cost).label("cost"),
    ).filter(ApiCallLog.created_at >= since).group_by(ApiCallLog.model).all()

    by_model = [
        {"model": r.model or "未知", "calls": r.calls, "cost": round(r.cost or 0, 6)}
        for r in model_rows
    ]

    # Daily breakdown
    daily = []
    for i in range(days - 1, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).date()
        d_str = d.isoformat()
        day_cost = db.query(func.sum(ApiCallLog.cost)).filter(
            func.date(ApiCallLog.created_at) == d_str
        ).scalar() or 0.0
        day_calls = db.query(func.count(ApiCallLog.id)).filter(
            func.date(ApiCallLog.created_at) == d_str
        ).scalar() or 0
        daily.append({"date": d_str, "cost": round(day_cost, 6), "calls": day_calls})

    return CostStatsResponse(
        total_cost=round(total_cost, 6),
        total_calls=total_calls,
        total_tokens=total_tokens or 0,
        by_model=by_model,
        daily=daily,
    ).model_dump()


@router.get("/rate-limit-config")
def get_rate_limit_config(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    configs = db.query(SystemConfig).filter(
        SystemConfig.key.in_(["rate_limit_max_per_day", "rate_limit_max_per_hour", "rate_limit_cooldown_minutes"])
    ).all()
    cfg_map = {c.key: c.value for c in configs}

    return RateLimitConfig(
        max_per_day=int(cfg_map.get("rate_limit_max_per_day", 2)),
        max_per_hour=int(cfg_map.get("rate_limit_max_per_hour", 10)),
        cooldown_minutes=int(cfg_map.get("rate_limit_cooldown_minutes", 1)),
    ).model_dump()


@router.put("/rate-limit-config")
def update_rate_limit_config(
    req: RateLimitConfig,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    entries = {
        "rate_limit_max_per_day": str(req.max_per_day),
        "rate_limit_max_per_hour": str(req.max_per_hour),
        "rate_limit_cooldown_minutes": str(req.cooldown_minutes),
    }
    for key, value in entries.items():
        cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if cfg:
            cfg.value = value
        else:
            db.add(SystemConfig(key=key, value=value))
    db.commit()
    return MessageResponse(message="限流配置已更新")
