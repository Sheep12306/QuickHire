from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependencies import get_db, require_admin
from models import User, ResumeVersion, InterviewAnswer, AdminUserNote, AdminAuditLog
from security import hash_password
from schemas import (
    AdminUserListItem, AdminUserDetail, BanUserRequest, ChangeRoleRequest,
    AdminUserNoteRequest, AdminUserNoteResponse, ResetPasswordRequest, MessageResponse,
    PaginatedResponse,
)
from datetime import datetime

router = APIRouter()


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    role: str = Query(""),
    status: str = Query(""),  # active / banned
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(User)

    if search:
        like = f"%{search}%"
        q = q.filter(
            (User.email.like(like)) |
            (User.display_name.like(like)) |
            (User.phone.like(like))
        )
    if role:
        q = q.filter(User.role == role)
    if status == "active":
        q = q.filter(User.is_active == True)
    elif status == "banned":
        q = q.filter(User.is_active == False)

    total = q.count()

    order_col = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        q = q.order_by(order_col.desc())
    else:
        q = q.order_by(order_col.asc())

    users = q.offset((page - 1) * size).limit(size).all()

    items = []
    for u in users:
        resume_count = db.query(func.count(ResumeVersion.id)).filter(
            ResumeVersion.user_id == u.id
        ).scalar() or 0
        items.append(AdminUserListItem(
            id=u.id,
            email=u.email,
            phone=u.phone,
            display_name=u.display_name,
            role=u.role or "user",
            is_active=u.is_active,
            membership_type=u.membership_type or "free",
            resume_count=resume_count,
            created_at=u.created_at.isoformat() if u.created_at else None,
            last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
        ).model_dump())

    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/export")
def export_users(
    format: str = Query("csv"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    users = db.query(User).order_by(User.id.desc()).all()
    rows = [
        {
            "id": u.id, "email": u.email or "", "phone": u.phone or "",
            "display_name": u.display_name or "", "role": u.role or "user",
            "is_active": u.is_active, "membership_type": u.membership_type or "free",
            "created_at": u.created_at.isoformat() if u.created_at else "",
        }
        for u in users
    ]
    return {"items": rows}


@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    resume_count = db.query(func.count(ResumeVersion.id)).filter(
        ResumeVersion.user_id == u.id
    ).scalar() or 0
    interview_count = db.query(func.count(InterviewAnswer.id)).filter(
        InterviewAnswer.user_id == u.id
    ).scalar() or 0
    optimize_count = db.query(func.count(ResumeVersion.id)).filter(
        ResumeVersion.user_id == u.id,
        ResumeVersion.optimized_content.isnot(None),
    ).scalar() or 0

    return AdminUserDetail(
        id=u.id,
        email=u.email,
        phone=u.phone,
        display_name=u.display_name,
        job_preference=u.job_preference,
        city=u.city,
        target_city=u.target_city,
        role=u.role or "user",
        is_active=u.is_active,
        banned_until=u.banned_until.isoformat() if u.banned_until else None,
        ban_reason=u.ban_reason,
        membership_type=u.membership_type or "free",
        membership_expires_at=u.membership_expires_at.isoformat() if u.membership_expires_at else None,
        last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
        created_at=u.created_at.isoformat() if u.created_at else None,
        updated_at=u.updated_at.isoformat() if u.updated_at else None,
        resume_count=resume_count,
        interview_count=interview_count,
        optimize_count=optimize_count,
    ).model_dump()


@router.patch("/{user_id}/ban")
def ban_user(
    user_id: int,
    req: BanUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    if u.role == "super_admin":
        raise HTTPException(status_code=403, detail="不能封禁超级管理员")

    u.is_active = False
    u.ban_reason = req.reason
    if req.duration_hours > 0:
        from datetime import timedelta
        u.banned_until = datetime.utcnow() + timedelta(hours=req.duration_hours)
    else:
        u.banned_until = None  # permanent

    # Audit log
    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="ban_user",
        target_type="user",
        target_id=user_id,
        detail=f"封禁用户, 原因: {req.reason}, 时长: {req.duration_hours}h",
    ))
    db.commit()
    return MessageResponse(message="用户已封禁")


@router.patch("/{user_id}/unban")
def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    u.is_active = True
    u.banned_until = None
    u.ban_reason = None

    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="unban_user",
        target_type="user",
        target_id=user_id,
        detail="解封用户",
    ))
    db.commit()
    return MessageResponse(message="用户已解封")


@router.patch("/{user_id}/role")
def change_user_role(
    user_id: int,
    req: ChangeRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    if req.role not in ("user", "super_admin", "operator", "viewer"):
        raise HTTPException(status_code=400, detail="无效的角色")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    old_role = u.role
    u.role = req.role

    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="change_role",
        target_type="user",
        target_id=user_id,
        detail=f"角色变更: {old_role} -> {req.role}",
    ))
    db.commit()
    return MessageResponse(message=f"角色已更新为 {req.role}")


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    u.password_hash = hash_password(req.new_password)

    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="reset_password",
        target_type="user",
        target_id=user_id,
        detail="重置密码",
    ))
    db.commit()
    return MessageResponse(message="密码已重置")


@router.get("/{user_id}/notes")
def get_user_notes(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    notes = (
        db.query(AdminUserNote)
        .filter(AdminUserNote.user_id == user_id)
        .order_by(AdminUserNote.created_at.desc())
        .all()
    )
    items = []
    for n in notes:
        admin_user = db.query(User).filter(User.id == n.admin_id).first()
        items.append(AdminUserNoteResponse(
            id=n.id,
            admin_id=n.admin_id,
            admin_name=admin_user.display_name or admin_user.email or "",
            note=n.note,
            created_at=n.created_at.isoformat() if n.created_at else None,
        ).model_dump())
    return {"items": items}


@router.post("/{user_id}/notes")
def add_user_note(
    user_id: int,
    req: AdminUserNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    note = AdminUserNote(
        user_id=user_id,
        admin_id=current_user.id,
        note=req.note,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return MessageResponse(message="备注已添加")


@router.get("/{user_id}/audit-log")
def get_user_audit_log(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(AdminAuditLog).filter(
        AdminAuditLog.target_type == "user",
        AdminAuditLog.target_id == user_id,
    )
    total = q.count()
    logs = q.order_by(AdminAuditLog.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = [{
        "id": log.id,
        "admin_user_id": log.admin_user_id,
        "action": log.action,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    } for log in logs]

    return {"total": total, "page": page, "size": size, "items": items}
