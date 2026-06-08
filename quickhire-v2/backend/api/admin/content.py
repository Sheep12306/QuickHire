from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import get_db, require_admin
from models import User, ResumeTemplate, PromptTemplate, Announcement, HelpArticle, AdminAuditLog
from schemas import (
    ResumeTemplateRequest, PromptTemplateRequest, AnnouncementRequest,
    HelpArticleRequest, MessageResponse,
)

router = APIRouter()


# ── Resume Templates ──────────────────────────────────────────

@router.get("/templates")
def list_templates(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(ResumeTemplate)
    if category:
        q = q.filter(ResumeTemplate.category == category)
    total = q.count()
    items = q.order_by(ResumeTemplate.sort_order.asc()).offset((page - 1) * size).limit(size).all()
    return {
        "total": total, "page": page, "size": size,
        "items": [{
            "id": t.id, "name": t.name, "description": t.description,
            "template_content": t.template_content, "thumbnail_url": t.thumbnail_url,
            "category": t.category, "is_active": t.is_active, "sort_order": t.sort_order,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        } for t in items]
    }


@router.post("/templates")
def create_template(
    req: ResumeTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    t = ResumeTemplate(**req.model_dump())
    db.add(t)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="create_template",
                         target_type="resume_template", target_id=0, detail=f"创建模板: {req.name}"))
    db.commit()
    db.refresh(t)
    return MessageResponse(message="模板已创建")


@router.put("/templates/{template_id}")
def update_template(
    template_id: int,
    req: ResumeTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    t = db.query(ResumeTemplate).filter(ResumeTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    for k, v in req.model_dump().items():
        setattr(t, k, v)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_template",
                         target_type="resume_template", target_id=template_id, detail=f"更新模板: {req.name}"))
    db.commit()
    return MessageResponse(message="模板已更新")


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    t = db.query(ResumeTemplate).filter(ResumeTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(t)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="delete_template",
                         target_type="resume_template", target_id=template_id))
    db.commit()
    return MessageResponse(message="模板已删除")


# ── Prompt Templates ──────────────────────────────────────────

@router.get("/prompts")
def list_prompts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    template_type: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(PromptTemplate)
    if template_type:
        q = q.filter(PromptTemplate.template_type == template_type)
    total = q.count()
    items = q.order_by(PromptTemplate.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return {
        "total": total, "page": page, "size": size,
        "items": [{
            "id": p.id, "name": p.name, "template_type": p.template_type, "content": p.content,
            "variables": p.variables, "is_default": p.is_default, "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        } for p in items]
    }


@router.post("/prompts")
def create_prompt(
    req: PromptTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    p = PromptTemplate(**req.model_dump())
    db.add(p)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="create_prompt",
                         target_type="prompt_template", detail=f"创建Prompt: {req.name}"))
    db.commit()
    db.refresh(p)
    return MessageResponse(message="Prompt模板已创建")


@router.put("/prompts/{prompt_id}")
def update_prompt(
    prompt_id: int,
    req: PromptTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    p = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prompt模板不存在")
    for k, v in req.model_dump().items():
        setattr(p, k, v)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_prompt",
                         target_type="prompt_template", target_id=prompt_id))
    db.commit()
    return MessageResponse(message="Prompt模板已更新")


@router.delete("/prompts/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    p = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prompt模板不存在")
    db.delete(p)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="delete_prompt",
                         target_type="prompt_template", target_id=prompt_id))
    db.commit()
    return MessageResponse(message="Prompt模板已删除")


# ── Announcements ─────────────────────────────────────────────

@router.get("/announcements")
def list_announcements(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(Announcement)
    total = q.count()
    items = q.order_by(Announcement.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return {
        "total": total, "page": page, "size": size,
        "items": [{
            "id": a.id, "title": a.title, "content": a.content, "priority": a.priority,
            "is_published": a.is_published,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        } for a in items]
    }


@router.post("/announcements")
def create_announcement(
    req: AnnouncementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    a = Announcement(**req.model_dump())
    db.add(a)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="create_announcement",
                         target_type="announcement", detail=f"创建公告: {req.title}"))
    db.commit()
    db.refresh(a)
    return MessageResponse(message="公告已创建")


@router.put("/announcements/{announcement_id}")
def update_announcement(
    announcement_id: int,
    req: AnnouncementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="公告不存在")
    for k, v in req.model_dump().items():
        setattr(a, k, v)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_announcement",
                         target_type="announcement", target_id=announcement_id))
    db.commit()
    return MessageResponse(message="公告已更新")


@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="公告不存在")
    db.delete(a)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="delete_announcement",
                         target_type="announcement", target_id=announcement_id))
    db.commit()
    return MessageResponse(message="公告已删除")


# ── Help Articles ─────────────────────────────────────────────

@router.get("/help")
def list_help_articles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(HelpArticle)
    if category:
        q = q.filter(HelpArticle.category == category)
    total = q.count()
    items = q.order_by(HelpArticle.sort_order.asc()).offset((page - 1) * size).limit(size).all()
    return {
        "total": total, "page": page, "size": size,
        "items": [{
            "id": h.id, "title": h.title, "content": h.content, "category": h.category,
            "tags": h.tags, "sort_order": h.sort_order, "is_published": h.is_published,
            "created_at": h.created_at.isoformat() if h.created_at else None,
            "updated_at": h.updated_at.isoformat() if h.updated_at else None,
        } for h in items]
    }


@router.post("/help")
def create_help_article(
    req: HelpArticleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    h = HelpArticle(**req.model_dump())
    db.add(h)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="create_help",
                         target_type="help_article", detail=f"创建帮助文章: {req.title}"))
    db.commit()
    db.refresh(h)
    return MessageResponse(message="帮助文章已创建")


@router.put("/help/{article_id}")
def update_help_article(
    article_id: int,
    req: HelpArticleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    h = db.query(HelpArticle).filter(HelpArticle.id == article_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="帮助文章不存在")
    for k, v in req.model_dump().items():
        setattr(h, k, v)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_help",
                         target_type="help_article", target_id=article_id))
    db.commit()
    return MessageResponse(message="帮助文章已更新")


@router.delete("/help/{article_id}")
def delete_help_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin", "operator"])),
):
    h = db.query(HelpArticle).filter(HelpArticle.id == article_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="帮助文章不存在")
    db.delete(h)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="delete_help",
                         target_type="help_article", target_id=article_id))
    db.commit()
    return MessageResponse(message="帮助文章已删除")
