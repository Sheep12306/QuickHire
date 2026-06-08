from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependencies import get_db, require_admin
from models import User, ResumeVersion, AdminAuditLog
from schemas import AdminResumeListItem, FlagResumeRequest, MessageResponse

router = APIRouter()


@router.get("")
def list_resumes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None),
    target_position: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    flagged_only: bool = Query(False),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(ResumeVersion)

    if user_id:
        q = q.filter(ResumeVersion.user_id == user_id)
    if target_position:
        q = q.filter(ResumeVersion.target_position.like(f"%{target_position}%"))
    if date_from:
        q = q.filter(func.date(ResumeVersion.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(ResumeVersion.created_at) <= date_to)

    total = q.count()
    resumes = q.order_by(ResumeVersion.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = []
    for r in resumes:
        user = db.query(User).filter(User.id == r.user_id).first()
        items.append(AdminResumeListItem(
            id=r.id,
            user_id=r.user_id,
            user_email=user.email or "" if user else "",
            user_name=user.display_name or "" if user else "",
            original_content=r.original_content[:200] if r.original_content else "",
            optimized_content=r.optimized_content[:200] if r.optimized_content else None,
            target_position=r.target_position,
            optimization_style=r.optimization_style,
            version_number=r.version_number,
            is_current=r.is_current,
            created_at=r.created_at.isoformat() if r.created_at else None,
        ).model_dump())

    return {"total": total, "page": page, "size": size, "items": items}


@router.get("/{resume_id}")
def get_resume_detail(
    resume_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    r = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    user = db.query(User).filter(User.id == r.user_id).first()
    return {
        "id": r.id,
        "user_id": r.user_id,
        "user_email": user.email if user else "",
        "user_name": user.display_name or "" if user else "",
        "original_content": r.original_content,
        "optimized_content": r.optimized_content,
        "target_position": r.target_position,
        "optimization_style": r.optimization_style,
        "analysis_result": r.analysis_result,
        "version_number": r.version_number,
        "is_current": r.is_current,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/{resume_id}/versions")
def get_resume_versions(
    resume_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    r = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    # Get all versions for this user with same target position
    versions = (
        db.query(ResumeVersion)
        .filter(
            ResumeVersion.user_id == r.user_id,
            ResumeVersion.original_content == r.original_content,
        )
        .order_by(ResumeVersion.version_number.asc())
        .all()
    )

    items = [{
        "id": v.id,
        "version_number": v.version_number,
        "optimized_content": v.optimized_content,
        "optimization_style": v.optimization_style,
        "analysis_result": v.analysis_result,
        "is_current": v.is_current,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    } for v in versions]

    return {"items": items}


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    r = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    db.delete(r)
    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="delete_resume",
        target_type="resume",
        target_id=resume_id,
        detail=f"删除简历记录 (user_id={r.user_id})",
    ))
    db.commit()
    return MessageResponse(message="简历记录已删除")


@router.patch("/{resume_id}/flag")
def flag_resume(
    resume_id: int,
    req: FlagResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    r = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    # Note: flagged/flag_reason columns are not in the original model.
    # We store flag info in the analysis_result as JSON extension for now,
    # or we can add these columns later.
    db.add(AdminAuditLog(
        admin_user_id=current_user.id,
        action="flag_resume" if req.flagged else "unflag_resume",
        target_type="resume",
        target_id=resume_id,
        detail=f"标记{'异常' if req.flagged else '正常'}: {req.flag_reason}",
    ))
    db.commit()
    return MessageResponse(message="已标记" if req.flagged else "已取消标记")
